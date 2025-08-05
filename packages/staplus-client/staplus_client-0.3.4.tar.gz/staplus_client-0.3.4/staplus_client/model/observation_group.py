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
from staplus_client import utils
from frost_sta_client.utils import check_datetime
from staplus_client.model import entity
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.observation_group import ObservationGroupDao
from staplus_client.model import license, party, campaign, relation, observation

class ObservationGroup(entity.Entity):

    def __init__(self,
                 name='',
                 description='',
                 purpose=None,
                 terms_of_use='',
                 privacy_policy=None,
                 creation_time=None,
                 end_time=None,
                 properties=None,
                 data_quality=None,
                 observations=None,
                 campaigns=None,
                 relations=None,
                 party=None,
                 license=None,
                 **kwargs):
        super().__init__(**kwargs)
        if properties is None:
            properties = {}
        self.name = name
        self.description = description
        self.purpose = purpose
        self.terms_of_use = terms_of_use
        self.privacy_policy = privacy_policy
        self.creation_time = creation_time
        self.end_time = end_time
        self.properties = properties
        self.data_quality = data_quality
        self.observations = observations
        self.campaigns = campaigns
        self.relations = relations
        self.party = party
        self.license = license

    def __new__(cls, *args, **kwargs):
        new_group = super().__new__(cls)
        attributes = {'_id': None, '_name': '', '_description': '', '_purpose': None, '_terms_of_use': '',
                      '_privacy_policy': None, '_creation_time': '', '_end_start': None,
                      '_properties': None, '_data_quality': None,
                      '_observations': None, '_relations': None, '_campaigns': None,
                      '_party': None, '_license': None,
                      '_self_link': '', '_service': None}
        for key, value in attributes.items():
            new_group.__dict__[key] = value
        return new_group

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
    def purpose(self):
        return self._purpose

    @purpose.setter
    def purpose(self, value):
        if value is None:
            self._purpose = None
            return
        if not isinstance(value, str):
            raise ValueError('purpose should be of type str!')
        self._purpose = value

    @property
    def terms_of_use(self):
        return self._terms_of_use

    @terms_of_use.setter
    def terms_of_use(self, value):
        if value is None:
            self._terms_of_use = None
            return
        if not isinstance(value, str):
            raise ValueError('termsOfUse should be of type str!')
        self._terms_of_use = value

    @property
    def privacy_policy(self):
        return self._privacy_policy

    @privacy_policy.setter
    def privacy_policy(self, value):
        if value is None:
            self._privacy_policy = None
            return
        if not isinstance(value, str):
            raise ValueError('privacyPolicy should be of type str!')
        self._privacy_policy = value

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, value):
        self._creation_time = check_datetime(value, 'creation_time')

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        if value is None:
            self._end_time = None
            return
        self._end_time = check_datetime(value, 'end_time')

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        if value is None:
            self._properties = {}
            return
        if not isinstance(value, dict):
            raise ValueError('properties should be of type dict!')
        self._properties = value

    @property
    def data_quality(self):
        return self._data_quality

    @data_quality.setter
    def data_quality(self, value):
        if value is None:
            self._data_quality = None
            return
        if not isinstance(value, dict):
            raise ValueError('dataQuality should be of type dict!')
        self._data_quality = value

    @property
    def observations(self):
        return self._observations

    @observations.setter
    def observations(self, values):
        if values is None:
            self._observations = None
            return
        if isinstance(values, list) and all(isinstance(os, observation.Observation) for os in values):
            entity_class = entity_type.EntityTypes['Observation']['class']
            self._observations = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(os, observation.Observation)) for os in values.entities):
            raise ValueError('observations should be a list of Observation')
        self._observations = values

    def get_observations(self):
        result = self.service.observations()
        result.parent = self
        return result

    @property
    def relations(self):
        return self._relations

    @relations.setter
    def relations(self, values):
        if values is None:
            self._relations = None
            return
        if isinstance(values, list) and all(isinstance(rs, relation.Relation) for rs in values):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self._relations = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(rs, relation.Relation)) for rs in values.entities):
            raise ValueError('relations should be a list of Relation')
        self._relations = values

    def get_relations(self):
        result = self.service.relations()
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
        if isinstance(values, list) and all(isinstance(ps, campaign.Campaign) for ps in values):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self._campaigns = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ps, campaign.Campaign)) for ps in values.entities):
            raise ValueError('campaigns should be a list of Campaign')
        self._campaigns = values

    def get_campaigns(self):
        result = self.service.campaigns()
        result.parent = self
        return result

    @property
    def party(self):
        return self._party

    @party.setter
    def party(self, value):
        if value is None or isinstance(value, party.Party):
            self._party = value
            return
        raise ValueError('party should be of type Party!')

    def get_party(self):
        result = self.service.party()
        result.parent = self
        return result

    @property
    def license(self):
        return self._license

    @license.setter
    def license(self, value):
        if value is None or isinstance(value, license.License):
            self._license = value
            return
        raise ValueError('license should be of type License!')

    def get_license(self):
        result = self.service.license()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        if self.observations is not None:
            self.observations.set_service(service)
        if self.relations is not None:
            self.relations.set_service(service)
        if self.campaigns is not None:
            self.campaigns.set_service(service)
        if self.party is not None:
            self.party.set_service(service)
        if self.license is not None:
            self.license.set_service(service)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        if id(self) == id(other):
            return True
        if self.name != other.name:
            return False
        if self.description != other.description:
            return False
        if self.purpose != other.purpose:
            return False
        if self.terms_of_use != other.terms_of_use:
            return False
        if self.privacy_policy != other.privacy_policy:
            return False
        if self.creation_time is not None and other.creation_time is not None and datetime.fromisoformat(self.creation_time) != datetime.fromisoformat(other.creation_time):
            return False
        if self.end_time is not None and other.end_time is not None and datetime.fromisoformat(self.end_time) != datetime.fromisoformat(other.end_time):
            return False
        if self.properties != other.properties:
            return False
        if self.data_quality != other.data_quality:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        data = super().__getstate__()
        if self.name is not None and self.name != '':
            data['name'] = self.name
        if self.description is not None and self.description != '':
            data['description'] = self.description
        if self.purpose is not None and self.purpose != '':
            data['purpose'] = self.purpose
        if self.terms_of_use is not None and self.terms_of_use != '':
            data['termsOfUse'] = self.terms_of_use
        if self.privacy_policy is not None and self.privacy_policy != '':
            data['privacyPolicy'] = self.privacy_policy
        if self.creation_time is not None:
            data['creationTime'] = datetime.fromisoformat(self.creation_time)
        if self.end_time is not None:
            data['endTime'] = datetime.fromisoformat(self.end_time)
        if self.properties is not None and self.properties != {}:
            data['properties'] = self.properties
        if self.data_quality is not None and self.data_quality != {}:
            data['dataQuality'] = self.data_quality
        if self.party is not None:
            data['Party'] = self.party
        if self.license is not None:
            data['License'] = self.license
        if self._observations is not None and len(self.observations.entities) > 0:
            data['Observations'] = self.observations.__getstate__()
        if self._relations is not None and len(self.relations.entities) > 0:
            data['Relations'] = self.relations.__getstate__()
        if self._campaigns is not None and len(self.campaigns.entities) > 0:
            data['Campaigns'] = self.campaigns.__getstate__()
        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        self.name = state.get("name", None)
        self.description = state.get("description", None)
        self.purpose = state.get("purpose", None)
        self.terms_of_use = state.get("termsOfUse", None)
        self.privacy_policy = state.get("privacyPolicy", None)
        self.creation_time = state.get("creationTime", None)
        self.end_time = state.get("endTime", None)
        self.properties = state.get("properties", None)
        self.data_quality = state.get("dataQuality", None)

        if state.get("Party", None) is not None:
            self.party = party.Party()
            self.party.__setstate__(state["Party"])
        if state.get("License", None) is not None:
            self.license = license.License()
            self.license.__setstate__(state["License"])

        if state.get("Observations", None) is not None and isinstance(state["Observations"], list):
            entity_class = entity_type.EntityTypes['Observation']['class']
            self.observations = utils.transform_json_to_entity_list(state['Observations'], entity_class)
            self.observations.next_link = state.get("Observations@iot.nextLink", None)
            self.observations.count = state.get("Observations@iot.count", None)
        if state.get("Campaigns", None) is not None and isinstance(state["Campaigns"], list):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self.campaigns = utils.transform_json_to_entity_list(state['Campaigns'], entity_class)
            self.campaigns.next_link = state.get("Campaigns@iot.nextLink", None)
            self.campaigns.count = state.get("Campaigns@iot.count", None)
        if state.get("Relations", None) is not None and isinstance(state["Relations"], list):
            entity_class = entity_type.EntityTypes['Relation']['class']
            self.relations = utils.transform_json_to_entity_list(state['Relations'], entity_class)
            self.relations.next_link = state.get("Relations@iot.nextLink", None)
            self.relations.count = state.get("Relations@iot.count", None)

    def get_dao(self, service):
        return ObservationGroupDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity