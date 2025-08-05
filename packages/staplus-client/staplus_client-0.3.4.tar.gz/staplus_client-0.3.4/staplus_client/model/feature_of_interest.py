from frost_sta_client.model import feature_of_interest
from staplus_client.dao.features_of_interest import FeaturesOfInterestDao

class FeatureOfInterest(feature_of_interest.FeatureOfInterest):

    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity

    def get_observations(self):
        result = self.service.observations()
        result.parent = self
        return result

    def get_dao(self, service):
        return FeaturesOfInterestDao(service)