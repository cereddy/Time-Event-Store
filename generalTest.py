
import unittest

from datetime import datetime
from eventStore import EventStore



class TestStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        store = EventStore()
        # clear the store
        collection = store.actualStore.eventCollection

        collection.drop()
        cls.store = store

    def test_set_get(self):

        date1a = datetime(year=2019, month=8, day=23, hour=9, minute=29)
        date1 = datetime(year=2019, month=8, day=23, hour=9, minute=30)
        date1b = datetime(year=2019, month=8, day=23, hour=9, minute=31)

        date2a = datetime(year=2019, month=8, day=23, hour=9, minute=44)
        date2 = datetime(year=2019, month=8, day=23, hour=9, minute=45)
        date2b = datetime(year=2019, month=8, day=23, hour=9, minute=46)

        date3a = datetime(year=2019, month=8, day=23, hour=10, minute=29)
        date3 = datetime(year=2019, month=8, day=23, hour=10, minute=30)
        date3b = datetime(year=2019, month=8, day=23, hour=10, minute=31)

        self.store.setEvent(at=date1, event="first event", level="INFO")
        self.store.setEvent(at=date2, event="second event", level="WARNING")
        self.store.setEvent(at=date3, event="third event", level="ERROR", tag="WEB")

        # test query by time
        res = self.store.getEvents(fromTime=date1a)
        self.assertTrue(isinstance(res, list))
        self.assertTrue(len(res)==3)
        
        # test query by time
        res = self.store.getEvents(fromTime=date1b, toTime=date2b)
        self.assertTrue(len(res)==1)
        evt1 = res[0]
        self.assertTrue(evt1['time'] == date2)
        self.assertTrue(evt1['event'] == "second event")
        self.assertTrue(evt1['level'] == "WARNING")
        
        # test query by other fields
        res = self.store.getEvents(otherQueries=[{'level': 'ERROR'}])
        self.assertTrue(len(res)==1)
        evt1 = res[0]
        self.assertTrue(evt1['time'] == date3)
        self.assertTrue(evt1['event'] == "third event")
        self.assertTrue('tag' in list(evt1.keys()))
        self.assertTrue(evt1['tag'] == "WEB")

    def test_set_read_only_mode(self):
        self.store.resetStore()
        self.store = EventStore(readOnly=True)
        dateAux = datetime(year=1999,month=12, day=10)
        dateAuxb = datetime(year=1999,month=12, day=11)
        with self.assertRaises(PermissionError):
            self.store.setEvent(at=dateAux, event="another event")
        
        res = self.store.getEvents(toTime=dateAuxb)
        self.assertTrue(len(res)==0)

        self.store.resetStore()
        self.store = EventStore()


    def test_time_zone(self):
        pass

    def testRegexClassif(self):
        pass


if __name__ == "__main__":
    unittest.main()