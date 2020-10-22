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

from flask import redirect, url_for
from flask_login import login_required

from .fetch import fetcher
from .metadata import metadata
from .proposal import proposals
from .singletons import app, ipfs


@app.route('/update/<uuid>', methods=['GET'])
@login_required
def update(uuid):
    proposal = proposals[uuid]
    try:
        metadata.check_for_conflicts(proposal)
    except:  # noqa
        return "sounds good, doesn't work"
    else:
        for whl in proposal:
            metadata.update(whl)
            print(ipfs.add(fetcher[whl]))
    finally:
        del proposals[proposal.uuid]
    return redirect(url_for('index'))
