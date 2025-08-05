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

EntityTypes = {
    'Datastream': {
        'singular': 'Datastream',
        'plural': 'Datastreams',
        'class': 'staplus_client.model.datastream.Datastream',
        'relations_list': ['Sensor', 'Thing', 'ObservedProperty', 'Observations', 'Party', 'License', 'Campaign']
    },
    'MultiDatastream': {
        'singular': 'MultiDatastream',
        'plural': 'MultiDatastreams',
        'class': 'staplus_client.model.multi_datastream.MultiDatastream',
        'relations_list': ['Sensor', 'Thing', 'ObservedProperties', 'Observations', 'Party', 'License', 'Campaign']
    },
    'FeatureOfInterest': {
        'singular': 'FeatureOfInterest',
        'plural': 'FeaturesOfInterest',
        'class': 'staplus_client.model.feature_of_interest.FeatureOfInterest',
        'relations_list': ['Observations']
    },
    'HistoricalLocation': {
        'singular': 'HistoricalLocation',
        'plural': 'HistoricalLocations',
        'class': 'staplus_client.model.historical_location.HistoricalLocation',
        'relations_list': ['Thing', 'Locations']
    },
    'Actuator': {
        'singular': 'Actuator',
        'plural': 'Actuators',
        'class': 'frost_sta_client.model.actuator.Actuator',
        'relations_list': ['TaskingCapabilities']
    },
    'Location': {
        'singular': 'Location',
        'plural': 'Locations',
        'class': 'staplus_client.model.location.Location',
        'relations_list': ['Things', 'HistoricalLocations']
    },
    'Observation': {
        'singular': 'Observation',
        'plural': 'Observations',
        'class': 'staplus_client.model.observation.Observation',
        'relations_list': ['FeatureOfInterest', 'Datastream', 'MultiDatastream', 'Subjects', 'Objects']
    },
    'Thing': {
        'singular': 'Thing',
        'plural': 'Things',
        'class': 'staplus_client.model.thing.Thing',
        'relations_list': ['Datastreams', 'MultiDatastreams', 'Locations', 'HistoricalLocations', 'TaskingCapabilities',
                           'Party']
    },
    'ObservedProperty': {
        'singular': 'ObservedProperty',
        'plural': 'ObservedProperties',
        'class': 'staplus_client.model.observedproperty.ObservedProperty',
        'relations_list': ['Datastreams', 'MultiDatastreams']
    },
    'Sensor': {
        'singular': 'Sensor',
        'plural': 'Sensors',
        'class': 'staplus_client.model.sensor.Sensor',
        'relations_list': ['Datastreams', 'MultiDatastreams']
    },
    'Task': {
        'singular': 'Task',
        'plural': 'Tasks',
        'class': 'frost_sta_client.model.task.Task',
        'relations_list': ['TaskingCapability']
    },
    'TaskingCapability': {
        'singular': 'TaskingCapability',
        'plural': 'TaskingCapabilities',
        'class': 'frost_sta_client.model.tasking_capability.TaskingCapability',
        'relations_list': ['Tasks', 'Actuator', 'Thing']
    },
    'UnitOfMeasurement': {
        'singular': 'UnitOfMeasurement',
        'plural': 'UnitOfMeasurements',
        'class': 'frost_sta_client.model.ext.unitofmeasurement.UnitOfMeasurement'
    },
    'EntityList': {
        'singular': 'EntityList',
        'plural': 'EntityLists',
        'class': 'staplus_client.model.ext.entity_list.EntityList'
    },
    #
    # STAplus
    #
    'Party': {
        'singular': 'Party',
        'plural': 'Parties',
        'class': 'staplus_client.model.party.Party',
        'relations_list': ['Datastreams', 'MultiDatastreams', 'Things', 'Campaigns', 'ObservationGroups']
    },
    'License': {
        'singular': 'License',
        'plural': 'Licenses',
        'class': 'staplus_client.model.license.License',
        'relations_list': ['Datastreams', 'MultiDatastreams', 'ObservationGroups', 'Campaigns']
    },
    'Campaign': {
        'singular': 'Campaign',
        'plural': 'Campaigns',
        'class': 'staplus_client.model.campaign.Campaign',
        'relations_list': ['Party', 'License', 'Datastreams', 'MultiDatastreams', 'ObservationGroups']
    },
    'ObservationGroup': {
        'singular': 'ObservationGroup',
        'plural': 'ObservationGroups',
        'class': 'staplus_client.model.observation_group.ObservationGroup',
        'relations_list': ['Party', 'License', 'Observations', 'Relations', 'Campaigns']
    },
    'Relation': {
        'singular': 'Relation',
        'plural': 'Relations',
        'class': 'staplus_client.model.relation.Relation',
        'relations_list': ['Subject', 'Object', 'ObservationGroups']
    }
}

list_for_class = {}
for key, entity_type in EntityTypes.items():
    list_for_class[entity_type["class"]] = entity_type["plural"]


def get_list_for_class(clazz):
    clazz_name = clazz.__module__ + "." + clazz.__name__
    return list_for_class[clazz_name]
