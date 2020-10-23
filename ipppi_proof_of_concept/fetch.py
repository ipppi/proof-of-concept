# Fetch and cache wheels
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

from functools import lru_cache
from os import makedirs
from os.path import basename, join
from tempfile import mkdtemp
from urllib.request import urlopen


class WheelFetcher:
    def __init__(self):
        self.dir = mkdtemp(prefix='ipppi-')  # this needs clean up

    @lru_cache(maxsize=None)
    def fetch(self, whl, uuid):
        filename = join(self.dir, uuid, basename(whl))
        makedirs(self.proposal_dir(uuid), exist_ok=True)
        with urlopen(whl) as fi, open(filename, 'wb') as fo:
            fo.write(fi.read())
        return filename

    def proposal_dir(self, uuid):
        return join(self.dir, uuid)


fetcher = WheelFetcher()
