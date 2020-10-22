# Check for conflicts
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

from os.path import basename, join
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from distlib.wheel import Wheel
from hasoil import has_conflict
from packaging.utils import canonicalize_name


def check_for_conflicts(wheels):
    with TemporaryDirectory() as d:
        versions, requirements = {}, []
        for whl in wheels:
            filename = join(d, basename(whl))
            with urlopen(whl) as fi, open(filename, 'wb') as fo:
                fo.write(fi.read())
            w = Wheel(filename)
            versions[canonicalize_name(w.name)] = w.version
            # Argh distlib.metadata.Metadata.dependencies is broken!
            requirements.extend(w.metadata.todict().get('requires_dist', []))
    print(versions, requirements)
    if has_conflict(versions, requirements): raise ValueError('conflicts!')
    print('OK!')  # Hey don't judge I'm in a hurry!
