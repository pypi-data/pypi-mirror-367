from frost_sta_client.dao.observation import ObservationDao as STAObservationDao
from staplus_client.dao.base import BaseDao as STAplusBaseDao
from staplus_client.query.query import Query
from staplus_client.model.ext.entity_type import EntityTypes

class ObservationDao(STAObservationDao):
    def __init__(self, service):
        """
        A data access object for operations with the Observation entity
        """
        super().__init__(service)
        entitytype = EntityTypes["Observation"]
        self.entitytype = entitytype["singular"]
        self.entitytype_plural = entitytype["plural"]
        self.entity_class = entitytype["class"]

    def query(self):
        return Query(self.service, self.entitytype, self.entitytype_plural, self.entity_class, self.parent)

    def create(self, entity):
        return STAplusBaseDao.create(self, entity)

class ObjectDao(ObservationDao):
    def __init__(self, service):
        """
        A data access object for operations with the Object entity
        """
        super().__init__(service)
        entitytype =  {
            'singular': 'Object',
            'plural': 'Relations',
            'class': 'staplus_client.model.observation.Observation',
            'relations_list': ['Subjects']
        }
        self.entitytype = entitytype["singular"]
        self.entitytype_plural = entitytype["plural"]
        self.entity_class = entitytype["class"]


class SubjectDao(ObservationDao):
    def __init__(self, service):
        """
        A data access object for operations with the Subject entity
        """
        super().__init__(service)
        entitytype =  {
            'singular': 'Subject',
            'plural': 'Relations',
            'class': 'staplus_client.model.observation.Observation',
            'relations_list': ['Objects']
        }
        self.entitytype = entitytype["singular"]
        self.entitytype_plural = entitytype["plural"]
        self.entity_class = entitytype["class"]

