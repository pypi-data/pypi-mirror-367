# Copyright (C) 2023-2024 Secure Dimensions GmbH, Munich, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from staplus_client.dao import base
from staplus_client.model.ext.entity_type import EntityTypes


class ObservationGroupDao(base.BaseDao):
    def __init__(self, service):
        """
        A data access object for operations with the ObservationGroup entity
        """
        base.BaseDao.__init__(self, service, EntityTypes["ObservationGroup"])
