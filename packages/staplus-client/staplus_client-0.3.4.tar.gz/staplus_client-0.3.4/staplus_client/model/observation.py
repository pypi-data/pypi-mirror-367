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

from datetime import datetime

from frost_sta_client.model import observation
from staplus_client import utils
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.observation import ObservationDao, SubjectDao, ObjectDao
from staplus_client.model import observation_group, relation


class Observation(observation.Observation):

    def __init__(self,
                 phenomenon_time=None,
                 result=None,
                 result_time=None,
                 result_quality=None,
                 valid_time=None,
                 parameters=None,
                 datastream=None,
                 multi_datastream=None,
                 feature_of_interest=None,
                 observation_groups=None,
                 subjects=None,
                 objects=None,
                 **kwargs):
        super().__init__(phenomenon_time, result, result_time, result_quality, valid_time,
                         parameters, datastream, multi_datastream, feature_of_interest, **kwargs)
        self.observation_groups = observation_groups
        self.subjects = subjects
        self.objects = objects

    def __new__(cls, *args, **kwargs):
        new_observation = super().__new__(cls, args, kwargs)
        attributes = {'_observation_groups': None, '_subjects': None, '_objects': None}
        for key, value in attributes.items():
            new_observation.__dict__[key] = value
        return new_observation

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
            raise ValueError('groups should be a list of ObservationGroup')
        self._observation_groups = values

    def get_observation_groups(self):
        result = self.service.observation_groups()
        result.parent = self
        return result

    @property
    def subjects(self):
        return self._subjects

    @subjects.setter
    def subjects(self, values):
        if values is None:
            self._subjects = None
            return
        if isinstance(values, list) and all(isinstance(rs, relation.Relation) for rs in values):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self._subjects = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(rs, relation.Relation)) for rs in values.entities):
            raise ValueError('subjects should be a list of Relation')
        self._subjects = values

    def get_subjects(self):
        result = self.service.subjects()
        result.parent = self
        return result

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, values):
        if values is None:
            self._objects = None
            return
        if isinstance(values, list) and all(isinstance(rs, relation.Relation) for rs in values):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self._objects = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(rs, relation.Relation)) for rs in values.entities):
            raise ValueError('objects should be a list of Relation')
        self._objects = values

    def get_objects(self):
        result = self.service.objects()
        result.parent = self
        return result

    def get_datastream(self):
        result = self.service.datastream()
        result.parent = self
        return result

    def get_multi_datastream(self):
        result = self.service.multi_datastream()
        result.parent = self
        return result

    def get_feature_of_interest(self):
        result = self.service.features_of_interest()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        super().ensure_service_on_children(service)
        if self.observation_groups is not None:
            self.observation_groups.set_service(service)
        if self.subjects is not None:
            self.subjects.set_service(service)
        if self.objects is not None:
            self.objects.set_service(service)

    def __getstate__(self):
        data = super().__getstate__()
        if self._observation_groups is not None and len(self.observation_groups.entities) > 0:
            data['ObservationGroups'] = self.observation_groups.__getstate__()
        if self._subjects is not None and len(self.subjects.entities) > 0:
            data['Subjects'] = self.subjects.__getstate__()
        if self._objects is not None and len(self.objects.entities) > 0:
            data['Objects'] = self.objects.__getstate__()
        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        if state.get("ObservationGroups", None) is not None and isinstance(state["ObservationGroups"], list):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self.observation_groups = utils.transform_json_to_entity_list(state['ObservationGroups'], entity_class)
            self.observation_groups.next_link = state.get("ObservationGroups@iot.nextLink", None)
            self.observation_groups.count = state.get("ObservationGroups@iot.count", None)
        if state.get("Subjects", None) is not None and isinstance(state["Subjects"], list):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self.subjects = utils.transform_json_to_entity_list(state['Subjects'], entity_class)
            self.subjects.next_link = state.get("Subjects@iot.nextLink", None)
            self.subjects.count = state.get("Subjects@iot.count", None)
        if state.get("Objects", None) is not None and isinstance(state["Objects"], list):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self.objects = utils.transform_json_to_entity_list(state['Objects'], entity_class)
            self.objects.next_link = state.get("Objects@iot.nextLink", None)
            self.objects.count = state.get("Objects@iot.count", None)

    def __eq__(self, other):
        if other is None or other == {}:
            return False
        if not isinstance(other, type(self)):
            return False
        if id(self) == id(other):
            return True
        if self.result != other.result:
            return False
        if datetime.fromisoformat(self.phenomenon_time) != datetime.fromisoformat(other.phenomenon_time):
            return False
        if self.result_time is not None and other.result_time is not None and datetime.fromisoformat(self.result_time) != datetime.fromisoformat(other.result_time):
            return False
        if self.valid_time is not None and other.valid_time is not None and datetime.fromisoformat(self.valid_time) != datetime.fromisoformat(other.valid_time):
            return False
        if self.parameters != other.parameters:
            return False
        if self.result_quality != other.result_quality:
            return False
        return True

    def get_dao(self, service):
        return ObservationDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
class Object(Observation):
    def get_dao(self, service):
        return ObjectDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
class Subject(Observation):
    def get_dao(self, service):
        return SubjectDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity