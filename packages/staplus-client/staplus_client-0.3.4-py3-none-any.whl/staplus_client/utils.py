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
import json

import geojson
import jsonpickle, sys

from staplus_client.model.ext.entity_list import EntityList
from staplus_client.model.thing import Thing
from frost_sta_client import utils


def transform_json_to_entity_list(json_response, entity_class):
    entity_list = EntityList(entity_class)
    response_list = []
    if isinstance(json_response, dict):
        try:
            response_list = json_response['value']
            entity_list.next_link = json_response.get("@iot.nextLink", None)
            entity_list.count = json_response.get("@iot.count", None)
        except AttributeError as e:
            raise e
    elif isinstance(json_response, list):
        response_list = json_response
    else:
        raise ValueError("expected json as a dict or list to transform into entity list")
    entity_list.entities = [transform_json_to_entity(item, entity_list.entity_class) for item in response_list]
    return entity_list


def transform_json_to_entity(json_response, entity_class):
    return utils.transform_json_to_entity(json_response, entity_class)

def transform_entity_to_json_dict(entity):
    data = utils.transform_entity_to_json_dict(entity)
    if 'feature' in data and type(data['feature']) != dict:
        data['feature'] = json.loads(geojson.dumps(entity.feature))
    if 'location' in data and type(data['location']) != dict:
        data['location'] = json.loads(geojson.dumps(entity.location))
    if type(entity) == Thing and entity.locations is not None and type(entity.locations) != dict:
        locations = []
        for l in entity.locations:
            location = transform_entity_to_json_dict(l)
            #location['location'] = json.loads(geojson.dumps(l.location))
            locations.append(location)

        data['Locations'] = locations

    return data

def class_from_string(string):
    return utils.class_from_string(string)