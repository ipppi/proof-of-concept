# Update the package index
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

from os.path import basename

from .metadata import metadata
from .singletons import app
from .static import simple_html


@app.route('/simple/', methods=['GET'])
def simple():
    return simple_html.format(''.join(
        f'<a href="/simple/{pkg}/">{pkg}</a><br>'
        for pkg in metadata.versions))


@app.route('/simple/<pkg>/', methods=['GET'])
def project(pkg):
    try:
        url = metadata.url(pkg)
    except IndexError:
        return simple_html.format('')
    else:
        return simple_html.format(f'<a href="{url}">{basename(url)}</a>')
