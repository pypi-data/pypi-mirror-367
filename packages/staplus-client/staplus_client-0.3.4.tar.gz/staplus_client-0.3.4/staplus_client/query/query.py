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



import staplus_client.utils
import staplus_client.model.ext.entity_list
from frost_sta_client.query import query

import logging
import requests
from requests.exceptions import JSONDecodeError


class Query(query.Query):
    def __init__(self, service, entity, entitytype_plural, entity_class, parent):
        super().__init__(service, entity, entitytype_plural, entity_class, parent)

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, service):
        if service is None:
            self._service = service
            return
        if not isinstance(service, staplus_client.service.staplusservice.STAplusService):
            raise ValueError('service should be of type STAplusService')
        self._service = service

    # exception: similar functions in basedao
    def list(self, callback=None, step_size=None):
        """
        Get an entity collection as a dictionary
        callbacks so far only work in combination with step_size. If step_size is set, then the callback function
        is called at every iteration of the step_size
        """
        url = self.service.get_full_path(self.parent, self.entitytype_plural)
        #slash = "" if str(furl.path).endswith('/') else "/"
        #if self.parent is None:
            #url = self.service.url.url + slash + self.entitytype_plural
        #else:
            #url = self.service.url.url + slash + self.entitytype_plural + '(' + str(self.parent.id) + ')/' + self.entity

        #url = furl(url)
        url.args = self.params
        try:
            response = self.service.execute('get', url)
        except requests.exceptions.HTTPError as e:
            error_json = e.response.json()
            error_message = error_json['message']
            logging.error("Query failed with status-code {}, {}".format(e.response.status_code, error_message))
            raise e
        logging.debug('Received response: {} from {}'.format(response.status_code, url))
        try:
            json_response = response.json()
        except JSONDecodeError:
            raise ValueError('Cannot find json in http response')
        entity_list = staplus_client.utils.transform_json_to_entity_list(json_response, self.entity_class)
        entity_list.set_service(self.service)

        entity_list.callback = callback
        entity_list.step_size = step_size

        return entity_list
    def item(self, callback=None, step_size=None):
        """
        Get an entity as a dictionary
        callbacks so far only work in combination with step_size. If step_size is set, then the callback function
        is called at every iteration of the step_size
        """
        url = self.service.get_full_path(self.parent, self.entity)
        #slash = "" if str(furl.path).endswith('/') else "/"
        #if self.parent is None:
            #url = self.service.url.url + slash + self.entitytype_plural
        #else:
            #url = self.service.url.url + slash + self.entitytype_plural + '(' + str(self.parent.id) + ')/' + self.entity

        #url = furl(url)
        url.args = self.params
        try:
            response = self.service.execute('get', url)
        except requests.exceptions.HTTPError as e:
            error_json = e.response.json()
            error_message = error_json['message']
            logging.error("Query failed with status-code {}, {}".format(e.response.status_code, error_message))
            raise e
        logging.debug('Received response: {} from {}'.format(response.status_code, url))
        try:
            json_response = response.json()
        except JSONDecodeError:
            raise ValueError('Cannot find json in http response')
        entity = staplus_client.utils.transform_json_to_entity(json_response, self.entity_class)
        entity.set_service(self.service)

        return entity
