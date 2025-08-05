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
from staplus_client.model import entity
from staplus_client.model import datastream, multi_datastream, thing, observation_group, campaign
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.party import PartyDao


class Party(entity.Entity):

    def __init__(self,
                 description=None,
                 auth_id=None,
                 role='',
                 display_name=None,
                 datastreams=None,
                 multi_datastreams=None,
                 things=None,
                 campaigns=None,
                 observation_groups=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.description = description
        self.auth_id = auth_id
        self.role = role
        self.display_name = display_name
        self.datastreams = datastreams
        self.multi_datastreams = multi_datastreams
        self.things = things
        self.campaigns = campaigns
        self.observation_groups = observation_groups

    def __new__(cls, *args, **kwargs):
        new_party = super().__new__(cls)
        attributes = {'_id': None, '_description': '', '_auth_id': '', '_role': '', '_display_name': '',
                      '_datastreams': None, '_multi_datastreams': None, '_things': None,
                      '_campaigns': None, '_observation_groups': None,
                      '_self_link': '', '_service': None}
        for key, value in attributes.items():
            new_party.__dict__[key] = value
        return new_party

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
    def auth_id(self):
        return self._auth_id

    @auth_id.setter
    def auth_id(self, value):
        if value is None:
            self._auth_id = None
            return
        if not isinstance(value, str):
            raise ValueError('authId should be of type str!')
        self._auth_id = value

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
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        if value is None:
            self._display_name = None
            return
        if not isinstance(value, str):
            raise ValueError('displayName should be of type str!')
        self._display_name = value

    @property
    def datastreams(self):
        return self._datastreams

    @datastreams.setter
    def datastreams(self, values):
        if values is None:
            self._datastreams = None
            return
        if isinstance(values, list) and all(isinstance(ds, datastream.Datastream) for ds in values):
            entity_class = entity_type.EntityTypes['Datastream']['class']
            self._datastreams = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ds, datastream.Datastream)) for ds in values.entities):
            raise ValueError('datastreams should be a list of datastreams')
        self._datastreams = values

    def get_datastreams(self):
        result = self.service.datastreams()
        result.parent = self
        return result

    @property
    def campaigns(self):
        return self._campaigns

    @campaigns.setter
    def campaigns(self, values):
        if values is None:
            self._campaigns = None
            return
        if isinstance(values, list) and all(isinstance(t, campaign.Campaign) for t in values):
            entity_class = entity_type.EntityTypes['CampaignThing']['class']
            self._campaigns = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(t, campaign.Campaign)) for t in values.entities):
            raise ValueError('campaigns should be a list of Campaign')
        self._things = values

    def get_campaigns(self):
        result = self.service.campaigns()
        result.parent = self
        return result

    @property
    def things(self):
        return self._things

    @things.setter
    def things(self, values):
        if values is None:
            self._things = None
            return
        if isinstance(values, list) and all(isinstance(t, thing.Thing) for t in values):
            entity_class = entity_type.EntityTypes['Thing']['class']
            self._things = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(t, thing.Thing)) for t in values.entities):
            raise ValueError('things should be a list of Thing')
        self._things = values

    def get_things(self):
        result = self.service.things()
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
        if isinstance(values, list) and all(isinstance(t, observation_group.ObservationGroup) for t in values):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self._observation_groups = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(t, observation_group.ObservationGroup)) for t in values.entities):
            raise ValueError('observation_groups should be a list of ObservationGroup')
        self._observation_groups = values

    def get_observation_groups(self):
        result = self.service.observation_groups()
        result.parent = self
        return result

    @property
    def multi_datastreams(self):
        return self._multi_datastreams

    @multi_datastreams.setter
    def multi_datastreams(self, values):
        if values is None:
            self._multi_datastreams = None
            return
        if isinstance(values, list) and all(isinstance(ds, multi_datastream.MultiDatastream) for ds in values):
            entity_class = entity_type.EntityTypes['MultiDatastream']['class']
            self._multi_datastreams = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ds, multi_datastream.MultiDatastream)) for ds in values.entities):
            raise ValueError('multi_datastreams should be a list of MultiDatastream')
        self._multi_datastreams = values

    def get_multi_datastreams(self):
        result = self.service.multi_datastreams()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        if self.datastreams is not None:
            self.datastreams.set_service(service)
        if self.multi_datastreams is not None:
            self.multi_datastreams.set_service(service)
        if self.campaigns is not None:
            self.campaigns.set_service(service)
        if self.observation_groups is not None:
            self.observation_groups.set_service(service)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        if id(self) == id(other):
            return True
        if self.auth_id != other.auth_id:
            return False
        if self.description != other.description:
            return False
        if self.role != other.role:
            return False
        if self.display_name != other.display_name:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        data = super().__getstate__()
        if self.auth_id is not None and self.auth_id != '':
            data['authId'] = self.auth_id
        if self.description is not None and self.description != '':
            data['description'] = self.description
        if self.role is not None and self.role != '':
            data['role'] = self.role
        if self.display_name is not None and self.display_name != '':
            data['displayName'] = self.display_name
        if self._datastreams is not None and len(self.datastreams.entities) > 0:
            data['Datastreams'] = self.datastreams.__getstate__()
        if self._multi_datastreams is not None and len(self.multi_datastreams.entities) > 0:
            data['MultiDatastreams'] = self.multi_datastreams.__getstate__()
        if self._things is not None and len(self.things.entities) > 0:
            data['Things'] = self.things.__getstate__()
        if self._campaigns is not None and len(self.campaigns.entities) > 0:
            data['Campaigns'] = self.campaigns.__getstate__()
        if self._observation_groups is not None and len(self.observation_groups.entities) > 0:
            data['ObservationGroups'] = self.observation_groups.__getstate__()
        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        self.auth_id = state.get("authId", None)
        self.description = state.get("description", None)
        self.role = state.get("role", None)
        self.display_name = state.get("displayName", None)

        if state.get("Datastreams", None) is not None and isinstance(state["Datastreams"], list):
            entity_class = entity_type.EntityTypes['Datastream']['class']
            self.datastreams = utils.transform_json_to_entity_list(state['Datastreams'], entity_class)
            self.datastreams.next_link = state.get("Datastreams@iot.nextLink", None)
            self.datastreams.count = state.get("Datastreams@iot.count", None)
        if state.get("MultiDatastreams", None) is not None and isinstance(state["MultiDatastreams"], list):
            entity_class = entity_type.EntityTypes['MultiDatastream']['class']
            self.multi_datastreams = utils.transform_json_to_entity_list(state['MultiDatastreams'], entity_class)
            self.multi_datastreams.next_link = state.get("MultiDatastreams@iot.nextLink", None)
            self.multi_datastreams.count = state.get("MultiDatastreams@iot.count", None)
        if state.get("Things", None) is not None and isinstance(state["Things"], list):
            entity_class = entity_type.EntityTypes['Thing']['class']
            self.things = utils.transform_json_to_entity_list(state['Things'], entity_class)
            self.things.next_link = state.get("Things@iot.nextLink", None)
            self.things.count = state.get("Things@iot.count", None)
        if state.get("Campaigns", None) is not None and isinstance(state["Campaigns"], list):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self.campaigns = utils.transform_json_to_entity_list(state['Campaigns'], entity_class)
            self.campaigns.next_link = state.get("Campaigns@iot.nextLink", None)
            self.campaigns.count = state.get("Campaigns@iot.count", None)
        if state.get("ObservationGroups", None) is not None and isinstance(state["ObservationGroups"], list):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self.observation_groups = utils.transform_json_to_entity_list(state['ObservationGroups'], entity_class)
            self.observation_groups.next_link = state.get("ObservationGroups@iot.nextLink", None)
            self.observation_groups.count = state.get("ObservationGroups@iot.count", None)

    def get_dao(self, service):
        return PartyDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity