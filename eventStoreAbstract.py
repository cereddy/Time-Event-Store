


class EventStoreAbstract:

    def __init__(self, *args, readOnly=True, timeAuto=True, **kwargs):

        self.eventStore = None
        self.setStore(*args, readOnly=readOnly, timeAuto=timeAuto, **kwargs)
    
    def setStore(self):
        raise NotImplementedError
    
    def storeEvent(self, at=None, event=None):
        raise NotImplementedError
    
    def storeEvents(self, listEvents):
        raise NotImplementedError

    def getEvents(self, *args, fromTime=None, toTime=None, **kwargs):
        raise NotImplementedError
    
