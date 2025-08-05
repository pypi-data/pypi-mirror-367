from frost_sta_client.model import sensor
class Sensor(sensor.Sensor):
    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
    
    def get_datastreams(self):
        result = self.service.datastreams()
        result.parent = self
        return result
    
    def get_multi_datastreams(self):
        result = self.service.multi_datastreams()
        result.parent = self
        return result