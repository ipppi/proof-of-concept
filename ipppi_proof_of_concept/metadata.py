# Metadata system
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

from distlib.wheel import Wheel
from hasoil import has_conflict
from packaging.utils import canonicalize_name

from .fetch import fetcher
from .singletons import pg


class MetadataSystem:
    def __init__(self, pg):
        self.pg = pg
        pg.run('CREATE TEMPORARY TABLE release ('
               ' pkg TEXT PRIMARY KEY, version TEXT)')
        pg.run('CREATE TEMPORARY TABLE dependency ('
               ' pkg TEXT PRIMARY KEY, requirement TEXT)')

    @property
    def versions(self):
        return dict(self.pg.run('SELECT * FROM release'))

    @property
    def requirements(self):
        return list(self.pg.run('SELECT requirement FROM dependency'))

    def load(self, whl):
        w = Wheel(fetcher[whl])
        return (canonicalize_name(w.name), w.version,
                # Argh distlib.metadata.Metadata.dependencies is broken!
                w.metadata.todict().get('requires_dist', []))

    def update(self, whl):
        pkg, version, req = self.load(whl)
        self.pg.run('DELETE FROM release WHERE pkg = :pkg', pkg=pkg)
        self.pg.run('INSERT INTO release (pkg, version)'
                    ' VALUES (:pkg, :version)', pkg=pkg, version=version)
        self.pg.run('DELETE FROM dependency WHERE pkg = :pkg', pkg=pkg)
        for r in req:
            self.pg.run('INSERT INTO dependency (pkg, requirement)'
                        ' VALUES (:pkg, :requirement)', pkg=pkg, req=r)

    def check_for_conflicts(self, wheels):
        versions, requirements = self.versions, self.requirements
        for whl in wheels:
            pkg, version, req = self.load(whl)
            versions[pkg] = version
            requirements.extend(req)
        print(versions, requirements)
        if has_conflict(versions, requirements): raise ValueError('conflicts!')
        print('OK!')  # Hey don't judge I'm in a hurry!


metadata = MetadataSystem(pg)
