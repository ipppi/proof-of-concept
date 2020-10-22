# Package update proposal handling
# Copyright (C) 2020  Nguyễn Gia Phong
#
# This file is part of IPPPI.
#
# IPPPI is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IPPPI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with IPPPI.  If not, see <https://www.gnu.org/licenses/>.

from uuid import uuid4

from flask import redirect, request, session, url_for
from flask_login import current_user, login_required

from .check import check_for_conflicts
from .singletons import app, pg
from .static import mine_html, propose_pkg_html, propose_whl_html, review_html


class Proposal:
    def __init__(self, pg, uuid, proposer=None):
        self.pg = pg
        self.uuid = uuid
        if proposer is not None:
            pg.run('INSERT INTO proposal (uuid, proposer)'
                   ' VALUES (:uuid, :proposer)',
                   uuid=uuid, proposer=proposer)
            self.proposer = proposer
        else:
            (self.proposer,), = pg.run('SELECT proposer FROM proposal'
                                       ' WHERE uuid = :uuid', uuid=uuid)

    def __iter__(self):
        return (whl for whl, in self.pg.run(
            'SELECT whl FROM whlupdate WHERE uuid = :uuid',
            uuid=self.uuid))

    def __getitem__(self, pkg):
        return self.pg.run('SELECT whl FROM whlupdate'
                           ' WHERE uuid = :uuid AND pkg = :pkg',
                           uuid=self.uuid, pkg=pkg)

    def __setitem__(self, pkg, whl):
        self.pg.run('INSERT INTO whlupdate (uuid, pkg, whl)'
                    ' VALUES (:uuid, :pkg, :whl)'
                    ' ON CONFLICT (uuid, pkg) DO UPDATE SET whl = :whl',
                    uuid=self.uuid, pkg=pkg, whl=whl)

    def __delitem__(self, pkg):
        self.pg.run('DELETE FROM whlupdate WHERE uuid = :uuid AND pkg = :pkg',
                    uuid=self.uuid, pkg=pkg)

    def set_status(self, conflicts):
        self.pg.run('UPDATE proposal SET conflict = :conflict'
                    ' WHERE uuid = :uuid',
                    uuid=self.uuid, conflict=conflicts)

    def to_html(self, review):
        (conflict,), = self.pg.run('SELECT conflict FROM proposal'
                                   ' WHERE uuid = :uuid', uuid=self.uuid)
        mark = '❌' if conflict else '✔️'
        updates = ''.join(f'<li>{pkg} @ {whl}</li>'
                          for pkg, whl in self.pg.run(
                              'SELECT pkg, whl FROM whlupdate'
                              ' WHERE uuid = :uuid',
                              uuid=self.uuid))
        if not review:
            return f'<p>{self.uuid} {mark}</p><ul>{updates}</ul>'
        button = ('<form action=review method=POST>'
                  f'<input type=submit name={self.uuid} value=approve></form>'
                  if current_user.is_maintainer else '')
        return (f'<p>{self.proposer}: {self.uuid} {mark}</p>'
                f'{button}<ul>{updates}</ul>')


class ProposalCollection:
    def __init__(self, pg):
        self.pg = pg
        pg.run('CREATE TEMPORARY TABLE proposal ('
               ' uuid TEXT PRIMARY KEY, proposer TEXT, conflict BOOL)')
        pg.run('CREATE TEMPORARY TABLE whlupdate ('
               ' uuid TEXT, pkg TEXT, whl TEXT,'
               ' PRIMARY KEY (uuid, pkg))')

    def __getitem__(self, uuid):
        return Proposal(self.pg, uuid)

    def __delitem__(self, uuid):
        self.pg.run('DELETE FROM proposal WHERE uuid = :uuid', uuid=uuid)
        self.pg.run('DELETE FROM whlupdate WHERE uuid = :uuid', uuid=uuid)

    def __iter__(self):
        for uuid, in self.pg.run('SELECT uuid FROM proposal'):
            yield Proposal(self.pg, uuid)

    def new(self):
        return Proposal(self.pg, uuid4().hex, current_user.get_id())

    def from_current_user(self):
        for uuid, in self.pg.run('SELECT uuid FROM proposal'
                                 ' WHERE proposer = :proposer',
                                 proposer=current_user.get_id()):
            yield Proposal(self.pg, uuid)


proposals = ProposalCollection(pg)


def genform(packages):
    for pkg in packages:
        yield f'<input type=text name={pkg} id={pkg} placeholder={pkg}><br>'


def render(proposal_listing, review=False):
    return ''.join(proposal.to_html(review) for proposal in proposal_listing)


@app.route('/propose_pkg', methods=['GET', 'POST'])
@login_required
def propose_pkg():
    if request.method == 'GET': return propose_pkg_html
    session['pkg'] = request.form['pkg'].split(',')
    return redirect(url_for('propose_whl'))


@app.route('/propose_whl', methods=['GET', 'POST'])
@login_required
def propose_whl():
    if request.method == 'GET':
        return propose_whl_html.format(
            ''.join(genform(session['pkg'])))
    proposal = proposals.new()
    for pkg, whl in request.form.items():
        if pkg != 'submit':  # I'm sorry UCSB!
            proposal[pkg] = whl
    try:
        check_for_conflicts(proposal)
    except:  # noqa
        proposal.set_status(conflicts=True)
    else:
        proposal.set_status(conflicts=False)
    return redirect(url_for('index'))


@app.route('/mine', methods=['GET'])
@login_required
def mine(): return mine_html.format(render(proposals.from_current_user()))


@app.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    if request.method == 'GET':
        return review_html.format(render(proposals, review=True))
    # Statically typed programmers hate this!
    uuid, = request.form.keys()
    return redirect(url_for('update', uuid=uuid))
