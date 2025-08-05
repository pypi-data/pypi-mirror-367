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

import logging
import requests

from staplus_client.service.staplusservice import STAplusService
from staplus_client.model.entity import Entity
from frost_sta_client.model.ext import entity_list

class EntityList(entity_list.EntityList):
    def __init__(self, entity_class, entities=None):
        super().__init__(entity_class, entities)

    def __next__(self):
        idx, next_entity = next(self.iterable_entities, (len(self.entities), None))
        if self.step_size is not None and idx is not None and idx % self.step_size == 0:
            self.callback(idx)
        if next_entity is not None:
            return next_entity
        if self.next_link is not None:
            try:
                response = self.service.execute('get', self.next_link)
            except requests.exceptions.HTTPError as e:
                error_json = e.response.json()
                error_message = error_json['message']
                logging.error("Query failed with status-code {}, {}".format(e.response.status_code, error_message))
                raise e
            logging.debug('Received response: {} from {}'.format(response.status_code, self.next_link))
            try:
                json_response = response.json()
            except ValueError:
                raise ValueError('Cannot find json in http response')

            result_list = staplus_client.utils.transform_json_to_entity_list(json_response, self.entity_class)
            self.entities += result_list.entities
            self.set_service(self.service)
            self.next_link = json_response.get("@iot.nextLink", None)
            self.iterable_entities = iter(enumerate(self.entities[-len(result_list.entities):], start=idx))
            return next(self.iterable_entities)[1]
        raise StopIteration

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        if value is None or isinstance(value, STAplusService):
            self._service = value
            return
        raise ValueError('service should be of type STAplusService')

    def set_service(self, service):
        self.service = service
        for entity in self.entities:
            entity.set_service(service)

    def entities(self, values):
        if isinstance(values, list) and all(isinstance(v, Entity) for v in values):
            self._entities = values
            return
        raise ValueError('entities should be a list of STAplus entities')