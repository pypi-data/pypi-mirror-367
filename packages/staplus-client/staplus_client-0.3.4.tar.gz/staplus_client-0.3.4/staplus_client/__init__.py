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

from staplus_client import model
from staplus_client import dao
from staplus_client import service
from staplus_client import query

from staplus_client.model.party import Party
from staplus_client.model.license import License
from staplus_client.model.thing import Thing
from staplus_client.model.datastream import Datastream
from staplus_client.model.multi_datastream import MultiDatastream
from staplus_client.model.campaign import Campaign
from staplus_client.model.relation import Relation
from staplus_client.model.observation_group import ObservationGroup
from staplus_client.model.observation import Observation
from staplus_client.model.feature_of_interest import FeatureOfInterest
from staplus_client.model.location import Location
from staplus_client.model.sensor import Sensor
from staplus_client.model.observedproperty import ObservedProperty
from staplus_client.model.historical_location import HistoricalLocation
from staplus_client.model.ext.entity_type import EntityTypes
from staplus_client.model.ext.unitofmeasurement import UnitOfMeasurement
from staplus_client.service.staplusservice import STAplusService

import jsonpickle
import demjson3

jsonpickle.load_backend('demjson3', 'encode', 'decode', 'JSONDecodeError')
jsonpickle.set_preferred_backend('demjson3')
jsonpickle.set_decoder_options("demjson3", decode_float=float)

from .__version__ import (__title__, __version__, __license__, __author__, __contact__, __url__,
                          __description__, __copyright__)
