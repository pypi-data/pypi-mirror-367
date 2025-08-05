# OGC STAplus (SensorThings) API Python Client

This STAplus Python Client implements the [STAplus](https://docs.ogc.org/is/22-022r1/22-022r1.html) API. The aim is to simplify development of STAplus and SensorThings enabled client applications.

**_NOTE:_** This implementation is an extension to the [FROST API Python Client](https://github.com/FraunhoferIOSB/FROST-Python-Client). To have better control over bug fixing and improvements, this implementation is actually based on a fork of the FROST API Python Client, hosted on a Secure Dimensions Github repository: [STA Python Client](https://github.com/securedimensions/STA-Python-Client).

## Python Version
This library requires Python 3.11 or better to support parsing ISO datetime values (`datetime.datetime.fromisoformat`). See [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) for more information.

## Features
* Support for all STAplus and SensorThings entity types
* CRUD operations
* Queries on entity lists
* Query on single entity
* MultiDatastreams
* Cloning Entities
* Fetching entities relative to an entity (using many-association)
* Fetching one single entity relative to an entity (using one-association)

## Installation via PyPi
Installation via pip: `pip install staplus-client`

## Limitations
This implementation has the following limitations for the Entity `Location` and `FeatureOfInterest`:

* `Location/location` must be a GeoJSON Geometry object (this is an Any in the SensorThings datamodel)
* `FeatureOfInterest/feature` must be a GeoJSON Object (this is an Any in the SensorThings datamodel)

For both entities, the `encodingType` attribute is not tested by the implementation. For interoperability with other applications, the value should be `application/geo+json`.

## API

The `STAplusService` class is central to the library. An instance of it represents a STAplus service and is identified by a URI.


### Creating Entities via the STAplus Client
The source code below demonstrates how to initialize the client for a STAplus endpoint on `url`. 

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staplus.STAplusService(url)
```

#### Configuring an Authentication Handler
When interacting with a STAplus service that has enabled authentication, the use of an `AuthHandler` is required.

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staPlus.STAplusService(url, auth_handler=auth)
```

#### Creating a Party Entity
The `Party` entity represents a user or an institution. When interacting with a STAplus service that has enabled authentication, the `Party` entity represents the acting user and access control controls Create, Update and Delete.
```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staPlus.STAplusService(url, auth_handler=auth)
ljs = staPlus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)
```

#### Creating a STAplus enriched Datastream
The STAplus `Datastream` is capable to have a `Party` and a `License` associated. Also, the `Thing` is associated to a `Party` entity.
```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staplus.STAplusService(url, auth_handler=auth)
ljs = staplus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)

# find the CC-BY license
cc_by = service.licenses().find('CC_BY')

# Create a thing associated to LJS
thing = staplus.Thing('Raspberry Pi', 'Raspberry Pi 4', )
thing.party = ljs

# Create a sensor
sensor = staplus.Sensor('air temperature sensor', 'SmartCitizen air temperature sensor', 'test/html', None,
                        'https://www.seeedstudio.com/Smart-Citizen-Starter-Kit-p-2865.html')

# Create a datastream associated to LJS with CC-BY license
datastream = staplus.Datastream('air temperature', 'air temperature measured with the SmartCitizen Kit',
                                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement', 
                                staplus.UnitOfMeasurement('Celsius', 'C', 'https://qudt.org/vocab/unit/DEG_C'))
datastream.observed_property = staplus.ObservedProperty('temperature', 'http://vocabs.lter-europe.net/EnvThes/22035',
                                            'air temperature')
datastream.party = ljs
datastream.thing = thing
datastream.sensor = sensor
datastream.license = cc_by

service.create(datastream)
```

#### Creating a few Observation entities
```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staplus.STAplusService(url, auth_handler=auth)
ljs = staplus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)

# The feature of interest
marienplatz = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [11.571831046,48.135666124]
    }
}
foi = staplus.FeatureOfInterest('Marienplatz', 'famous place in Munich', 'application/vnd.geo+json', marienplatz)

# The temperature
observation = staplus.Observation("2023-07-02T15:34:00Z", 20, "2023-07-02T15:34:00Z")
observation.feature_of_interest = foi
observation.datastream = service.datastreams().find(<the datastream id created previously>)

service.create(observation)

observation = staplus.Observation("2023-07-02T15:34:10Z", 21, "2023-07-02T15:34:10Z")
observation.feature_of_interest = foi
observation.datastream = service.datastreams().find(<the datastream id created previously>)

service.create(observation)
```

#### Creating an ObservationGroup Entity
A `ObservationGroup` entity can be used as a container of observations that belong together.

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staPlus.STAplusService(url, auth_handler=auth)
ljs = staPlus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)
group = staPlus.ObservationGroup("Marienplatz", "observations on Marienplatz", "none", "")
group.creation_time = parse_datetime("2023-07-02T15:35:00Z")
# Add all the observations that are associated to the FoI named 'Marienplatz'
group.observations = service.observations().query().filter("FeatureOfInterest/name eq 'Marienplatz'").list()
group.license = service.licenses().find('CC_BY')
group.party = ljs

service.create(group)
```

#### Creating SensorThings Entities
How to use this implementation on SensorThings Entity Types, please see the [FROST-Python-Client](https://github.com/securedimensions/STAplus-Python-Client) documentation.

### Fetching Entities via the STAplus Client
This implementation supports the fetching of `EntityList` and `Entity`.

#### Fetching an EntityList
An `EntityList` is the result from fetching entities that have a multiplicity `0..*` or `1..*`. To fetch the list of entities, you need to use the `.list()` function. The following example fetches all datastreams:

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staplus.STAplusService(url)
datastreams = service.datastreams().query().list()
```

In order to get all entities of a given entity, you can use the function `get_<entity_plural>()`. For example, to fetch all datastreams of a given `Thing` please use the following code: 

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staplus.STAplusService(url)
thing = service.things().find(1)
thing_datastreams = thing.get_datastreams().query().list()
```

#### Fetching an Entity
An `Entity` is the result from fetching an entity that has multiplicity `0..1` or `1`. To fetch one single entity you need to use the `.item()` function. The following example fetches the thing associated to a datastream:

```python
import staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staplus.STAplusService(url)
datastream = service.datastreams().find(1).item()
datastream_thing = datastream.get_thing().query().item()
```

### Cloning an Entity
When creating an Entity, mandatory entities can be provided either inline or by reference. To support the referencing of existing entities, the `clone()` function can be used. `clone()` returns a copy of the entity but only containing the `@iot.id`. This is important when preparing MQTT messages to publish observations.

#### Example ObservationGroup with inline entities
```JSON
{
  "Observations": [
    {
      "Datastream": {
        "@iot.id": 1,
        "description": "desc",
        "name": "new name",
        "observationType": "OM_Observation",
        "observedArea": {
          "coordinates": [11.509234, 48.110728],
          "type": "Point"
        },
        "phenomenonTime": "2023-07-24T06:30:18+00:00/2023-09-14T05:40:25.292000+00:00",
        "resultTime": "2023-07-24T06:30:18+00:00/2023-07-24T06:31:42+00:00",
        "unitOfMeasurement": { "definition": "...", "name": "n", "symbol": "n" }
      },
      "FeatureOfInterest": {
        "@iot.id": 77,
        "description": "A rainy place",
        "encodingType": "application/geo+json",
        "feature": { "coordinates": [-6.22299, 53.306816], "type": "Point" },
        "name": "Dublin",
        "properties": {
          "datastreams": [1, 2, 76, 2, 78, 77],
          "multi_datastreams": [11]
        }
      },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 19.111,
      "resultTime": "2024-05-02T19:36:06+00:00"
    },
    {
      "Datastream": {
        "@iot.id": 2,
        "description": "air relative humidity measured with the SmartCitizen Kit",
        "name": "Relative Humidity",
        "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
        "observedArea": {
          "coordinates": [11.509234, 48.110728],
          "type": "Point"
        },
        "phenomenonTime": "2023-07-24T06:30:18+00:00/2023-07-24T06:31:42+00:00",
        "resultTime": "2023-07-24T06:30:18+00:00/2023-07-24T06:31:42+00:00",
        "unitOfMeasurement": {
          "definition": "https://qudt.org/vocab/unit/PERCENT",
          "name": "Percentage",
          "symbol": "%"
        }
      },
      "FeatureOfInterest": {
        "@iot.id": 77,
        "description": "A rainy place",
        "encodingType": "application/geo+json",
        "feature": { "coordinates": [-6.22299, 53.306816], "type": "Point" },
        "name": "Dublin",
        "properties": {
          "datastreams": [1, 2, 76, 2, 78, 77],
          "multi_datastreams": [11]
        }
      },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 43.0,
      "resultTime": "2024-05-02T19:36:06+00:00"
    },
    {
      "Datastream": {
        "@iot.id": 76,
        "description": "Precipitation measured with the FT-0310 Weather Station",
        "name": "Rain",
        "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
        "unitOfMeasurement": {
          "definition": "https://qudt.org/vocab/unit/MilliM",
          "name": "millimiter",
          "symbol": "mm"
        }
      },
      "FeatureOfInterest": {
        "@iot.id": 77,
        "description": "A rainy place",
        "encodingType": "application/geo+json",
        "feature": { "coordinates": [-6.22299, 53.306816], "type": "Point" },
        "name": "Dublin",
        "properties": {
          "datastreams": [1, 2, 76, 2, 78, 77],
          "multi_datastreams": [11]
        }
      },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 87.0,
      "resultTime": "2024-05-02T19:36:06+00:00"
    },
    {
      "Datastream": {
        "@iot.id": 77,
        "description": "Wind direction measured with the FT-0310 Weather Station",
        "name": "Wind direction",
        "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
        "unitOfMeasurement": {
          "definition": "https://qudt.org/vocab/unit/DEG",
          "name": "degree",
          "symbol": "deg"
        }
      },
      "FeatureOfInterest": {
        "@iot.id": 77,
        "description": "A rainy place",
        "encodingType": "application/geo+json",
        "feature": { "coordinates": [-6.22299, 53.306816], "type": "Point" },
        "name": "Dublin",
        "properties": {
          "datastreams": [1, 2, 76, 2, 78, 77],
          "multi_datastreams": [11]
        }
      },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 241.0,
      "resultTime": "2024-05-02T19:36:06+00:00"
    },
    {
      "FeatureOfInterest": {
        "@iot.id": 77,
        "description": "A rainy place",
        "encodingType": "application/geo+json",
        "feature": { "coordinates": [-6.22299, 53.306816], "type": "Point" },
        "name": "Dublin",
        "properties": {
          "datastreams": [1, 2, 76, 2, 78, 77],
          "multi_datastreams": [11]
        }
      },
      "MultiDatastream": {
        "@iot.id": 11,
        "ObservedProperties": [
          {
            "@iot.id": 105,
            "definition": "http://vocab.nerc.ac.uk/standard_name/wind_speed/",
            "description": "Wind speed",
            "name": "wspeed"
          },
          {
            "@iot.id": 106,
            "definition": "http://vocab.nerc.ac.uk/standard_name/wind_gust_from_direction/",
            "description": "Wind gust",
            "name": "wgust"
          }
        ],
        "description": "Wind speed average and gust measured with the FT-0310 Weather Station",
        "multiObservationDataTypes": [
          "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
          "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"
        ],
        "name": "Wind speed avg and gust",
        "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_ComplexObservation",
        "unitOfMeasurements": [
          {
            "definition": "https://qudt.org/vocab/unit/M-PER-SEC",
            "name": "Meters per second",
            "symbol": "m/s"
          },
          {
            "definition": "https://qudt.org/vocab/unit/M-PER-SEC",
            "name": "Meters per second",
            "symbol": "m/s"
          }
        ]
      },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": [0.0, 0.0],
      "resultTime": "2024-05-02T19:36:06+00:00"
    }
  ],
  "Party": {
    "@iot.id": "36fd7ca4-08bb-11ef-b156-a337e8ef4d15",
    "displayName": "LJS",
    "role": "individual"
  },
  "creationTime": "2024-05-02T19:36:06+00:00",
  "description": " ",
  "endTime": "2024-05-02T19:36:06+00:00",
  "name": "OG 2024-05-02T19:36:06+00:00"
}
```

This example with inline `Datastream` and `FeatureOfInterest` entities has the size of 6245 Bytes.

#### Example ObservationGroup with referencing entities
```JSON
{
  "Observations": [
    {
      "Datastream": { "@iot.id": 1 },
      "FeatureOfInterest": { "@iot.id": 77 },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 19.111,
      "resultTime": "2024-05-03T09:48:33+00:00"
    },
    {
      "Datastream": { "@iot.id": 2 },
      "FeatureOfInterest": { "@iot.id": 77 },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 43.0,
      "resultTime": "2024-05-03T09:48:33+00:00"
    },
    {
      "Datastream": { "@iot.id": 76 },
      "FeatureOfInterest": { "@iot.id": 77 },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 87.0,
      "resultTime": "2024-05-03T09:48:33+00:00"
    },
    {
      "Datastream": { "@iot.id": 77 },
      "FeatureOfInterest": { "@iot.id": 77 },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": 241.0,
      "resultTime": "2024-05-03T09:48:33+00:00"
    },
    {
      "FeatureOfInterest": { "@iot.id": 77 },
      "MultiDatastream": { "@iot.id": 11 },
      "phenomenonTime": "2024-04-13T19:57:08+00:00",
      "result": [0.0, 0.0],
      "resultTime": "2024-05-03T09:48:33+00:00"
    }
  ],
  "Party": {
    "@iot.id": "4cd42a10-0932-11ef-919f-57f24e9b90e3",
    "displayName": "LJS",
    "role": "individual"
  },
  "creationTime": "2024-05-03T09:48:33+00:00",
  "description": " ",
  "endTime": "2024-05-03T09:48:33+00:00",
  "name": "OG 2024-05-03T09:48:33+00:00"
}
```

This example with referenced `Datastream` and `FeatureOfInterest` entities has the size of 1420 Bytes.
