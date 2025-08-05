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
import staplus_client
from frost_sta_client.model import thing

from staplus_client.dao.thing import ThingDao
from staplus_client.model import party
from staplus_client.model import location
from staplus_client.model.ext import entity_list, entity_type

class Thing(thing.Thing):

    def __init__(self,
                 name='',
                 description='',
                 properties=None,
                 locations=None,
                 historical_locations=None,
                 datastreams=None,
                 multi_datastreams=None,
                 tasking_capabilities=None,
                 party=None,
                 **kwargs):
        super().__init__(name, description, properties, locations, historical_locations,
                         datastreams, multi_datastreams, tasking_capabilities, **kwargs)
        self.party = party

    def __new__(cls, *args, **kwargs):
        new_thing = super().__new__(cls, args, kwargs)
        attributes = {'_party': None}
        for key, value in attributes.items():
            new_thing.__dict__[key] = value
        return new_thing

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

    def get_locations(self):
        result = self.service.locations()
        result.parent = self
        return result

    def get_historical_locations(self):
        result = self.service.historical_locations()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        super().ensure_service_on_children(service)
        if self.party is not None:
            self.party.set_service(service)

    def __getstate__(self):
        data = super().__getstate__()
        if self.party is not None:
            data['Party'] = self.party

        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        if state.get("Party", None) is not None:
            self.party = party.Party()
            self.party.__setstate__(state["Party"])

    def locations(self, values):
        if values is None:
            self._locations = None
            return
        if isinstance(values, list) and all(isinstance(loc, location.Location) for loc in values):
            entity_class = entity_type.EntityTypes['Location']['class']
            self._locations = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(loc, location.Location)) for loc in values.entities):
            raise ValueError('locations should be a list of locations')
        self._locations = values

    def get_dao(self, service):
        return ThingDao(service)
          
    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity