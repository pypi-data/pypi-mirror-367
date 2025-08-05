from frost_sta_client.model.ext import unitofmeasurement

class UnitOfMeasurement(unitofmeasurement.UnitOfMeasurement):
    def __init__(self, name="", symbol="", definition=""):
        super().__init__(name, symbol, definition)