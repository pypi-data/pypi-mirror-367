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

from frost_sta_client.utils import check_datetime
from staplus_client.utils import transform_json_to_entity_list
from staplus_client.model import entity, datastream, multi_datastream, license, observation_group, party
from staplus_client.model.ext import entity_list, entity_type
from staplus_client.dao.campaign import CampaignDao


class Campaign(entity.Entity):

    def __init__(self,
                 name='',
                 description='',
                 classification=None,
                 terms_of_use=None,
                 privacy_policy=None,
                 creation_time=None,
                 start_time=None,
                 end_time=None,
                 url=None,
                 properties=None,
                 datastreams=None,
                 multi_datastreams=None,
                 observation_groups=None,
                 party=None,
                 license=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.classification = classification
        self.terms_of_use = terms_of_use
        self.privacy_policy = privacy_policy
        self.creation_time = creation_time
        self.start_time = start_time
        self.end_time = end_time
        self.url = url
        self.properties = properties
        self.datastreams = datastreams
        self.multi_datastreams = multi_datastreams
        self.observation_groups = observation_groups
        self.party = party
        self.license = license

    def __new__(cls, *args, **kwargs):
        new_campaign = super().__new__(cls)
        attributes = {'_id': None, '_name': '', '_description': '', '_classification': None, '_terms_of_use': '',
                      '_privacy_statement': None, '_creation_time': '', '_start_time': None, '_end_start': None,
                      '_url': None, '_properties': None,
                      '_datastreams': None, '_multi_datastreams': None, 'observation_groups': None,
                      '_party': None, '_license': None,
                      '_self_link': '', '_service': None}
        for key, value in attributes.items():
            new_campaign.__dict__[key] = value
        return new_campaign

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
    def classification(self):
        return self._classification

    @classification.setter
    def classification(self, value):
        if value is None:
            self._classification = None
            return
        if not isinstance(value, str):
            raise ValueError('classification should be of type str!')
        self._classification = value

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
        if value is None:
            self._creation_time = None
            return
        self._creation_time = check_datetime(value, 'creation_time')

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if value is None:
            self._start_time = None
            return
        self._start_time = check_datetime(value, 'start_time')

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
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if value is None:
            self._url = None
            return
        if not isinstance(value, str):
            raise ValueError('url should be of type str!')
        self._url = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        if value is None:
            self._properties = None
            return
        if not isinstance(value, dict):
            raise ValueError('properties should be of type dict')
        self._properties = value

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

    @property
    def observation_groups(self):
        return self._observation_groups

    @observation_groups.setter
    def observation_groups(self, values):
        if values is None:
            self._observation_groups = None
            return
        if isinstance(values, list) and all(isinstance(gs, observation_group.ObservationGroup) for gs in values):
            entity_class = entity_type.EntityTypes['ObservationGroups']['class']
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

    def get_licence(self):
        result = self.service.license()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        if self.datastreams is not None:
            self.datastreams.set_service(service)
        if self.multi_datastreams is not None:
            self.multi_datastreams.set_service(service)
        if self.observation_groups is not None:
            self.observation_groups.set_service(service)
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
        if self.classification != other.classification:
            return False
        if self.terms_of_use != other.terms_of_use:
            return False
        if self.privacy_policy != other.privacy_policy:
            return False
        if self.creation_time is not None and other.creation_time is not None and datetime.fromisoformat(self.creation_time) != datetime.fromisoformat(other.creation_time):
            return False
        if self.start_time is not None and other.start_time is not None and datetime.fromisoformat(self.start_time) != datetime.fromisoformat(other.start_time):
            return False
        if self.end_time is not None and other.end_time is not None and datetime.fromisoformat(self.end_time) != datetime.fromisoformat(other.end_time):
            return False
        if self.url != other.url:
            return False
        if self.properties != other.properties:
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
        if self.classification is not None and self.classification != '':
            data['classification'] = self.classification
        if self.terms_of_use is not None and self.terms_of_use != '':
            data['termsOfUse'] = self.terms_of_use
        if self.privacy_policy is not None and self.privacy_policy != '':
            data['privacyPolicy'] = self.privacy_policy
        if self.creation_time is not None:
            data['creationTime'] = datetime.fromisoformat(self.creation_time)
        if self.start_time is not None:
            data['startTime'] = datetime.fromisoformat(self.start_time)
        if self.end_time is not None:
            data['endTime'] = datetime.fromisoformat(self.end_time)
        if self.url is not None and self.url != '':
            data['url'] = self.url
        if self.properties is not None and self.terms_of_use != {}:
            data['properties'] = self.properties
        if self._datastreams is not None and len(self.datastreams.entities) > 0:
            data['Datastreams'] = self.datastreams.__getstate__()
        if self._multi_datastreams is not None and len(self.multi_datastreams.entities) > 0:
            data['MultiDatastreams'] = self.multi_datastreams.__getstate__()
        if self._observation_groups is not None and len(self.observation_groups.entities) > 0:
            data['ObservationGroups'] = self.observation_groups.__getstate__()
        if self._party is not None:
            data['Party'] = self.party
        if self._license is not None:
            data['License'] = self.license
        return data

    def __setstate__(self, state):
        super().__setstate__(state)

        self.name = state.get("name", None)
        self.description = state.get("description", None)
        self.classification = state.get("classification", None)
        self.terms_of_use = state.get("termsOfUse", None)
        self.privacy_policy = state.get("privacyPolicy", None)
        self.creation_time = state.get("creationTime", None)
        self.start_time = state.get("startTime", None)
        self.end_time = state.get("endTime", None)
        self.properties = state.get("properties", None)
        self.url = state.get("url", None)

        if state.get("Datastreams", None) is not None and isinstance(state["Datastreams"], list):
            entity_class = entity_type.EntityTypes['Datastream']['class']
            self.datastreams = transform_json_to_entity_list(state['Datastreams'], entity_class)
            self.datastreams.next_link = state.get("Datastreams@iot.nextLink", None)
            self.datastreams.count = state.get("Datastreams@iot.count", None)
        if state.get("MultiDatastreams", None) is not None and isinstance(state["MultiDatastreams"], list):
            entity_class = entity_type.EntityTypes['MultiDatastream']['class']
            self.multi_datastreams = transform_json_to_entity_list(state['MultiDatastreams'], entity_class)
            self.multi_datastreams.next_link = state.get("MultiDatastreams@iot.nextLink", None)
            self.multi_datastreams.count = state.get("MultiDatastreams@iot.count", None)
        if state.get("Party", None) is not None:
            self.party = party.Party()
            self.party.__setstate__(state["Party"])
        if state.get("License", None) is not None:
            self.license = license.License()
            self.license.__setstate__(state["License"])
        if state.get("ObservationGroups", None) is not None and isinstance(state["ObservationGroups"], list):
            entity_class = entity_type.EntityTypes['ObservationGroup']['class']
            self.observation_groups = transform_json_to_entity_list(state['ObservationGroups'], entity_class)
            self.observation_groups.next_link = state.get("ObservationGroups@iot.nextLink", None)
            self.observation_groups.count = state.get("ObservationGroups@iot.count", None)

    def get_dao(self, service):
        return CampaignDao(service)

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity