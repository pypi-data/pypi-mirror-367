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
from staplus_client.model import entity, campaign, datastream, multi_datastream, observation_group
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.license import LicenseDao


class License(entity.Entity):

    def __init__(self,
                 name='',
                 definition='',
                 description=None,
                 attribution_text=None,
                 logo=None,
                 datastreams=None,
                 multi_datastreams=None,
                 campaigns=None,
                 observation_groups=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.definition = definition
        self.attribution_text = attribution_text
        self.logo = logo
        self.datastreams = datastreams
        self.multi_datastreams = multi_datastreams
        self.campaigns = campaigns
        self.observation_groups = observation_groups

    def __new__(cls, *args, **kwargs):
        new_license = super().__new__(cls)
        attributes = {'_id': None, '_name': '', '_description': '', '_definition': '',
                      '_logo': '', '_attribution_text': '',
                      '_datastreams': None, '_multi_datastreams': None,
                      '_campaigns': None, '_observation_groups': None,
                      '_self_link': '', '_service': None}
        for key, value in attributes.items():
            new_license.__dict__[key] = value
        return new_license

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            self._name = None
            return
        if not isinstance(value, str):
            raise ValueError('name should be of type str!')
        self._name = value

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
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, value):
        if value is None:
            self._definition = None
            return
        if not isinstance(value, str):
            raise ValueError('definition should be of type str!')
        self._definition = value

    @property
    def logo(self):
        return self._logo

    @logo.setter
    def logo(self, value):
        if value is None:
            self._value = None
            return
        if not isinstance(value, str):
            raise ValueError('logo should be of type str!')
        self._logo = value

    @property
    def attribution_text(self):
        return self._attribution_text

    @attribution_text.setter
    def attribution_text(self, value):
        if value is None:
            self._attribution_text = None
            return
        if not isinstance(value, str):
            raise ValueError('attributionText should be of type str!')
        self._attribution_text = value

    @property
    def observation_groups(self):
        return self._observation_groups

    @observation_groups.setter
    def observation_groups(self, values):
        if values is None:
            self._observation_groups = None
            return
        if isinstance(values, list) and all(isinstance(cs, observation_group.ObservationGroup) for cs in values):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self._observation_groups = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ds, observation_group.ObservationGroup)) for ds in values.entities):
            raise ValueError('observation_groups should be a list of ObservationGroup')
        self._observation_groups = values

    def get_observation_groups(self):
        result = self.service.observation_groups()
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
        if isinstance(values, list) and all(isinstance(cs, campaign.Campaign) for cs in values):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self._campaigns = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ds, campaign.Campaign)) for ds in values.entities):
            raise ValueError('campaigns should be a list of Campaign')
        self._campaigns = values

    def get_campaigns(self):
        result = self.service.campaigns()
        result.parent = self
        return result

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
            raise ValueError('datastreams should be a list of Datastream')
        self._datastreams = values

    def get_datastreams(self):
        result = self.service.datastreams()
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
        if self.campaigns is not None:
            self.campaigns.set_service(service)
        if self.observation_groups is not None:
            self.observation_groups.set_service(service)
        if self.datastreams is not None:
            self.datastreams.set_service(service)
        if self.multi_datastreams is not None:
            self.multi_datastreams.set_service(service)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        if id(self) == id(other):
            return True
        if self.name != other.name:
            return False
        if self.attribution_text != other.attribution_text:
            return False
        if self.definition != other.definition:
            return False
        if self.description != other.description:
            return False
        if self.logo != other.logo:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        data = super().__getstate__()
        if self.description is not None and self.description != '':
            data['description'] = self.description
        if self.definition is not None and self.definition != '':
            data['definition'] = self.definition
        if self.logo is not None and self.logo != '':
            data['logo'] = self.logo
        if self.attribution_text is not None and self.attribution_text != '':
            data['attributionText'] = self.attribution_text
        if self._datastreams is not None and len(self.datastreams.entities) > 0:
            data['Datastreams'] = self.datastreams.__getstate__()
        if self._multi_datastreams is not None and len(self.multi_datastreams.entities) > 0:
            data['MultiDatastreams'] = self.multi_datastreams.__getstate__()
        if self._campaigns is not None and len(self.campaigns.entities) > 0:
            data['Campaigns'] = self.campaigns.__getstate__()
        if self._observation_groups is not None and len(self.observation_groups.entities) > 0:
            data['ObservationGroups'] = self.observation_groups.__getstate__()
        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        self.name = state.get("name", None)
        self.description = state.get("description", None)
        self.definition = state.get("definition", None)
        self.logo = state.get("logo", None)
        self.attribution_text = state.get("attributionText", None)

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
        return LicenseDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity