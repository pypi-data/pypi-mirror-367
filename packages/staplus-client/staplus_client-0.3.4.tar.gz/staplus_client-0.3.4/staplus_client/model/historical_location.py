from frost_sta_client.model import historical_location
from staplus_client.dao.historical_location import HistoricalLocationDao

class HistoricalLocation(historical_location.HistoricalLocation):
    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
    
    def get_thing(self):
        result = self.service.thing()
        result.parent = self
        return result
    
    def get_locations(self):
        result = self.service.locations()
        result.parent = self
        return result
    
    def get_dao(self, service):
        return HistoricalLocationDao(service)
