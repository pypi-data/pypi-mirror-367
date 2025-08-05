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

import requests

from staplus_client.service.auth_handler import AuthHandler as STAplusAuthHandler
from frost_sta_client.service.auth_handler import AuthHandler as STAAuthHandler
from frost_sta_client.service import sensorthingsservice

from staplus_client.dao import observedproperty
from staplus_client.dao import historical_location
from staplus_client.dao import location
from staplus_client.dao import features_of_interest
from staplus_client.dao import datastream
from staplus_client.dao import observation_group
from staplus_client.dao import license
from staplus_client.dao import multi_datastream
from staplus_client.dao import observation
from staplus_client.dao import party
from staplus_client.dao import campaign
from staplus_client.dao import relation
from staplus_client.dao import thing
from staplus_client.dao import sensor
import staplus_client.model.ext.entity_type as staplus_entity_type

class STAplusService(sensorthingsservice.SensorThingsService):
    def __init__(self, url, auth_handler=None):
        super().__init__(url, auth_handler)

    def create(self, entity):
        return entity.get_dao(self).create(entity)

    def update(self, entity):
        entity.get_dao(self).update(entity)

    def patch(self, entity, patches):
        entity.get_dao(self).patch(entity, patches)

    def delete(self, entity):
        entity.get_dao(self).delete(entity)

    @property
    def auth_handler(self):
        return self._auth_handler

    @auth_handler.setter
    def auth_handler(self, value):
        if value is None:
            self._auth_handler = None
            return
        if (not isinstance(value, STAplusAuthHandler) and ( not isinstance(value, STAAuthHandler))):
            raise ValueError('auth should be of type AuthHandler!')
        self._auth_handler = value

    def execute(self, method, url, **kwargs):
        if self.auth_handler is not None:
            response = requests.request(method, url, auth=self.auth_handler.add_auth_header(), **kwargs)
        else:
            response = requests.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise e

        return response

    def get_path(self, parent, relation):
        if parent is None:
            return relation
        this_entity_type = staplus_entity_type.get_list_for_class(type(parent))
        #this_entity_type = staplus_entity_type.EntityTypes[relation]['plural'] if relation in staplus_entity_type.EntityTypes.keys() else staplus_entity_type.get_list_for_class(type(parent))
        if type(parent.id) == str:
            return "{entity_type}('{id}')/{relation}".format(entity_type=this_entity_type, id=parent.id, relation=relation)
        else:
            return "{entity_type}({id})/{relation}".format(entity_type=this_entity_type, id=parent.id, relation=relation)

    def party(self):
        return party.PartyDao(self)

    def parties(self):
        return party.PartyDao(self)

    def license(self):
        return license.LicenseDao(self)

    def licenses(self):
        return license.LicenseDao(self)

    def thing(self):
        return thing.ThingDao(self)

    def things(self):
        return thing.ThingDao(self)

    def sensor(self):
        return sensor.SensorDao(self)

    def sensors(self):
        return sensor.SensorDao(self)

    def datastream(self):
        return datastream.DatastreamDao(self)

    def datastreams(self):
        return datastream.DatastreamDao(self)

    def multi_datastream(self):
        return multi_datastream.MultiDatastreamDao(self)

    def multi_datastreams(self):
        return multi_datastream.MultiDatastreamDao(self)

    def observed_property(self):
        return observedproperty.ObservedPropertyDao(self)

    def observed_properties(self):
        return observedproperty.ObservedPropertyDao(self)

    def features_of_interest(self):
        return features_of_interest.FeaturesOfInterestDao(self)

    def historical_locations(self):
        return historical_location.HistoricalLocationDao(self)

    def locations(self):
        return location.LocationDao(self)

    def observations(self):
        return observation.ObservationDao(self)

    def campaigns(self):
        return campaign.CampaignDao(self)

    def relations(self):
        return relation.RelationDao(self)

    def subjects(self):
        return relation.SubjectsDao(self)

    def subject(self):
        return observation.SubjectDao(self)

    def objects(self):
        return relation.ObjectsDao(self)

    def object(self):
        return observation.ObjectDao(self)

    def observation_groups(self):
        return observation_group.ObservationGroupDao(self)
