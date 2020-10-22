# Singletons for convenient use (it's ugly I know)
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

from secrets import token_bytes

import ipfshttpclient
import pg8000
from flask import Flask

app = Flask(__name__)
app.secret_key = token_bytes()
pg = pg8000.connect('postgres', password='postgres')
ipfs = ipfshttpclient.connect()  # this should be closed
