
from eventStoreNoSql.eventStoreNoSql import EventStoreNoSql
class EventStore:
    """
    This abstraction is to make the instanciation of the store once per process : 
    Once the store has been set once, the other calls will only be using the same instance,
    without needing to set the store and its configuration again 

    """

    # actual store access object
    actualStore = None

    # defaults to instantiate a mongodb store
    def __init__(self, typeStore="nosql", **config):
        if not EventStore.actualStore:
            self.initStore(typeStore, **config)
    
    def __getattr__(self, val):
        return getattr(self.actualStore, val)
    
    def resetStore(self):
        EventStore.actualStore = None

    def initStore(self, typeStore, **config):
        if typeStore=='nosql':
            EventStore.actualStore = EventStoreNoSql()
            EventStore.actualStore.setStore(**config)
        else:
            raise ValueError('You must define a correct type of store')

    # for autocompletion purposes
    def setEvent(self, *args, **kwargs):
        return self.actualStore.storeEvent(*args, **kwargs)
    def getEvents(self, *args, **kwargs):
        return self.actualStore.getEvents(*args, **kwargs)