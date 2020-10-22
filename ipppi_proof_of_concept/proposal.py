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
from .static import propose_names_html, propose_versions_html


class Proposal:
    def __init__(self, pg, uuid):
        self.pg = pg
        self.uuid = uuid

    def __getitem__(self, project):
        return self.pg.run('SELECT version FROM proposal'
                           ' WHERE uuid = :uuid AND project = :project',
                           uuid=self.uuid, project=project)

    def __setitem__(self, project, version):
        self.pg.run('INSERT INTO proposal (uuid, project, version)'
                    ' VALUES (:uuid, :project, :version)'
                    ' ON CONFLICT (uuid, project)'
                    ' DO UPDATE SET version = :version',
                    uuid=self.uuid, project=project, version=version)


class ProposalCollection:
    def __init__(self, pg):
        self.pg = pg
        self.pg.run('CREATE TEMPORARY TABLE proposal ('
                    ' uuid TEXT, project TEXT, version TEXT,'
                    ' PRIMARY KEY (uuid, project))')

    def __getitem__(self, uuid):
        return Proposal(self.pg, uuid)

    def new(self):
        return self[uuid4()]


proposals = ProposalCollection(pg)


def genform(names):
    for name in names:
        yield f'<input type=text name={name} id={name} placeholder={name}><br>'


@app.route('/propose_names', methods=['GET', 'POST'])
@login_required
def propose_names():
    if request.method == 'GET': return propose_names_html
    session['names'] = request.form['names'].split(',')
    return redirect(url_for('propose_versions'))


@app.route('/propose_versions', methods=['GET', 'POST'])
@login_required
def propose_versions():
    if request.method == 'GET':
        return propose_versions_html.format(
            ''.join(genform(session['names'])))
    proposal = proposals.new()
    for name in request.form:
        if name != 'submit':  # I'm sorry UCSB!
            proposal[name] = request.form[name]
    return redirect(url_for('index'))
