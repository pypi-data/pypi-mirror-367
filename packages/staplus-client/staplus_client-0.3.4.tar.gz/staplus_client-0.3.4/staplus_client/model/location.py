from frost_sta_client.model import location
from staplus_client.dao.location import LocationDao

class Location(location.Location):

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
    
    def get_things(self):
        result = self.service.things()
        result.parent = self
        return result
    
    def get_historical_locations(self):
        result = self.service.historical_locations()
        result.parent = self
        return result

    def get_dao(self, service):
        return LocationDao(service)