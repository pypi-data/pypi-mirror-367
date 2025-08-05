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
from staplus_client.query.query import Query


class RelationDao(base.BaseDao):
    def __init__(self, service):
        """
        A data access object for operations with the Relation entity
        """
        base.BaseDao.__init__(self, service, EntityTypes["Relation"])

class SubjectsDao(base.BaseDao):
    def __init__(self, service):
        """
        A data access object for operations with the Subjects entity
        """
        base.BaseDao.__init__(self, service, {
            'singular': '-',
            'plural': 'Subjects',
            'class': 'staplus_client.model.relation.Relation',
            'relations_list': ['Object']
        })

    def query(self):
        return Query(self.service, self.entitytype, self.entitytype_plural, self.entity_class, self.parent)


class ObjectsDao(base.BaseDao):
    def __init__(self, service):
        """
        A data access object for operations with the Objects entity
        """
        base.BaseDao.__init__(self, service,  {
            'singular': '-',
            'plural': 'Objects',
            'class': 'staplus_client.model.relation.Relation',
            'relations_list': ['Subject']
        })

    def query(self):
        return Query(self.service, self.entitytype, self.entitytype_plural, self.entity_class, self.parent)
