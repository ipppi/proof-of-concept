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

from flask import redirect, request, session, url_for
from flask_login import login_required

from .singletons import app
from .static import propose_names_html, propose_versions_html


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
    for name in request.form:
        if name == 'submit': continue  # I'm sorry UCSB!
    return redirect(url_for('index'))
