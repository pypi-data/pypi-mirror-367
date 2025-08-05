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

from frost_sta_client.dao.multi_datastream import MultiDatastreamDao as STAMultiDatastreamDao
from staplus_client.dao.base import BaseDao as STAplusBaseDao
from staplus_client.query.query import Query
from staplus_client.model.ext.entity_type import EntityTypes

class MultiDatastreamDao(STAMultiDatastreamDao):
    def __init__(self, service):
        """
        A data access object for operations with the MultiDatastream entity
        """
        super().__init__(service)
        entitytype = EntityTypes["MultiDatastream"]
        self.entitytype = entitytype["singular"]
        self.entitytype_plural = entitytype["plural"]
        self.entity_class = entitytype["class"]

    def query(self):
        return Query(self.service, self.entitytype, self.entitytype_plural, self.entity_class, self.parent)

    def create(self, entity):
        return STAplusBaseDao.create(self, entity)