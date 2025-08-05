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

import staplus_client.query.query
import staplus_client.utils

import logging
import requests
from furl import furl

from frost_sta_client.utils import extract_value
from frost_sta_client.dao.base import BaseDao as STABaseDao
import staplus_client.utils

class BaseDao(STABaseDao):
    """
    The STAplus extension
    """
    APPLICATION_JSON_PATCH = {'Content-type': 'application/json-patch+json'}

    def __init__(self, service, entitytype):
        super().__init__(service, entitytype)

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        if value is None or isinstance(value, staplus_client.service.staplusservice.STAplusService):
            self._service = value
            return
        raise ValueError('service should be of type STAplusService')

    def create(self, entity):
        url = furl(self.service.url)
        url.path.add(self.entitytype_plural)
        logging.debug('Posting to ' + str(url.url))
        json_dict = staplus_client.utils.transform_entity_to_json_dict(entity)
        try:
            response = self.service.execute('post', url, json=json_dict)
        except requests.exceptions.HTTPError as e:
            error_json = e.response.json()
            error_message = error_json['message']
            logging.error("Creating {} failed with status-code {}, {}".format(type(entity).__name__,
                                                                            e.response.status_code,
                                                                            error_message))
            raise e
        entity.id = extract_value(response.headers['location'])
        entity.service = self.service
        id = "('" + entity.id + "')" if type(entity.id) == str else'(' + str(entity.id) + ')'
        entity.self_link = url.url + id
        logging.debug('Received response: ' + str(response.status_code))
        return entity.id

    def query(self):
        return staplus_client.query.query.Query(self.service, self.entitytype, self.entitytype_plural,
                                                  self.entity_class, self.parent)
