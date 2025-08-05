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

from staplus_client import utils
from staplus_client.model import entity, observation_group, observation
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.relation import RelationDao, SubjectsDao, ObjectsDao


class Relation(entity.Entity):

    def __init__(self,
                 description=None,
                 role='',
                 external_resource=None,
                 properties=None,
                 subject=None,
                 object=None,
                 observation_groups=None,
                 **kwargs):
        super().__init__(**kwargs)
        if properties is None:
            properties = {}
        self.description = description
        self.role = role
        self.external_resource = external_resource
        self.properties = properties
        self.subject = subject
        self.object = object
        self.observation_groups = observation_groups

    def __new__(cls, *args, **kwargs):
        new_relation = super().__new__(cls)
        attributes = {'_id': None, '_description': '', '_role': '',
                      '_external_resource': None, '_properties': None,
                      '_subject': None, '_object': None, '_observation_groups': None,
                      '_self_link': '', '_service': None}
        for key, value in attributes.items():
            new_relation.__dict__[key] = value
        return new_relation

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is None:
            self._description = None
            return
        if not isinstance(value, str):
            raise ValueError('description should be of type str!')
        self._description = value

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        if value is None:
            self._role = None
            return
        if not isinstance(value, str):
            raise ValueError('role should be of type str!')
        self._role = value

    @property
    def external_resource(self):
        return self._external_resource

    @external_resource.setter
    def external_resource(self, value):
        if value is None:
            self._external_resource = None
            return
        if not isinstance(value, str):
            raise ValueError('externalObject should be of type str!')
        self._external_resource = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        if value is None:
            self._properties = {}
            return
        if not isinstance(value, dict):
            raise ValueError('properties should be of type dict')
        self._properties = value

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        if value is None:
            self._subject = None
            return
        if not isinstance(value, observation.Observation):
            raise ValueError('subject should be of type Observation!')
        self._subject = value

    def get_subject(self):
        result = self.service.subject()
        result.parent = self
        return result

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self, value):
        if value is None:
            self._object = None
            return
        if not isinstance(value, observation.Observation):
            raise ValueError('object should be of type Observation!')
        self._object = value

    def get_object(self):
        result = self.service.object()
        result.parent = self
        return result

    @property
    def observation_groups(self):
        return self._observation_groups

    @observation_groups.setter
    def observation_groups(self, values):
        if values is None:
            self._observation_groups = None
            return
        if isinstance(values, list) and all(isinstance(gs, observation_group.ObservationGroup) for gs in values):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self._observation_groups = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(gs, observation_group.ObservationGroup)) for gs in values.entities):
            raise ValueError('observation_groups should be a list of ObservationGroup')
        self._observation_groups = values

    def get_observation_groups(self):
        result = self.service.observation_groups()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        if self.subject is not None:
            self.subject.set_service(service)
        if self.object is not None:
            self.object.set_service(service)
        if self.observation_groups is not None:
            self.observation_groups.set_service(service)

    def __eq__(self, other):
        if other is None:
            return False
        if id(self) == id(other):
            return True
        if self.role != other.role:
            return False
        if self.description != other.description:
            return False
        if self.external_resource != other.external_resource:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        data = super().__getstate__()
        if self.role is not None and self.role != '':
            data['role'] = self.role
        if self.description is not None and self.description != '':
            data['description'] = self.description
        if self.external_resource is not None and self.external_resource != {}:
            data['externalResource'] = self.external_resource
        if self.properties is not None and self.properties != {}:
            data['properties'] = self.properties
        if self.subject is not None and self.subject != {}:
            data['Subject'] = self.subject
        if self.object is not None and self.object != {}:
            data['Object'] = self.object
        if self._observation_groups is not None and len(self.observation_groups.entities) > 0:
            data['ObservationGroups'] = self.observation_groups.__getstate__()

        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        self.description = state.get("description", None)
        self.role = state.get("role", None)
        self.external_resource = state.get("externalResource", None)
        self.subject = state.get("Subject", None)
        self.object = state.get("Object", None)

        if state.get("ObservationGroups", None) is not None and isinstance(state["ObservationGroups"], list):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self.observation_groups = utils.transform_json_to_entity_list(state['ObservationGroups'], entity_class)
            self.observation_groups.next_link = state.get("ObservationGroups@iot.nextLink", None)
            self.observation_groups.count = state.get("ObservationGroups@iot.count", None)

    def get_dao(self, service):
        return RelationDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity

class Objects(Relation):
    def get_dao(self, service):
        return ObjectsDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
class Subjects(Relation):
    def get_dao(self, service):
        return SubjectsDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity