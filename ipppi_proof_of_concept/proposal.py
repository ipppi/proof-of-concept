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
from flask_login import login_required

from .singletons import app, pg
from .static import propose_pkg_html, propose_ver_html


class Proposal:
    def __init__(self, pg, uuid):
        self.pg = pg
        self.uuid = uuid

    def __getitem__(self, pkg):
        return self.pg.run('SELECT version FROM proposal'
                           ' WHERE uuid = :uuid AND pkg = :pkg',
                           uuid=self.uuid, pkg=pkg)

    def __setitem__(self, pkg, version):
        self.pg.run('INSERT INTO proposal (uuid, pkg, version)'
                    ' VALUES (:uuid, :pkg, :version)'
                    ' ON CONFLICT (uuid, pkg)'
                    ' DO UPDATE SET version = :version',
                    uuid=self.uuid, pkg=pkg, version=version)


class ProposalCollection:
    def __init__(self, pg):
        self.pg = pg
        self.pg.run('CREATE TEMPORARY TABLE proposal ('
                    ' uuid TEXT, pkg TEXT, version TEXT,'
                    ' PRIMARY KEY (uuid, pkg))')

    def __getitem__(self, uuid):
        return Proposal(self.pg, uuid)

    def new(self):
        return self[uuid4()]


proposals = ProposalCollection(pg)


def genform(packages):
    for pkg in packages:
        yield f'<input type=text name={pkg} id={pkg} placeholder={pkg}><br>'


@app.route('/propose_pkg', methods=['GET', 'POST'])
@login_required
def propose_pkg():
    if request.method == 'GET': return propose_pkg_html
    session['pkg'] = request.form['pkg'].split(',')
    return redirect(url_for('propose_versions'))


@app.route('/propose_versions', methods=['GET', 'POST'])
@login_required
def propose_versions():
    if request.method == 'GET':
        return propose_ver_html.format(
            ''.join(genform(session['pkg'])))
    proposal = proposals.new()
    for pkg, version in request.form.items():
        if pkg != 'submit':  # I'm sorry UCSB!
            proposal[pkg] = version
    return redirect(url_for('index'))
