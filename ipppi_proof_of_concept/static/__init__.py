# Static data
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

from importlib.resources import path


def read(resource):
    with path('ipppi_proof_of_concept.static', resource) as p:
        with open(p) as f: return f.read()


index_html = read('index.html')
register_html = read('register.html')
login_html = read('login.html')
propose_pkg_html = read('propose_pkg.html')
propose_whl_html = read('propose_whl.html')
