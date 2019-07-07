

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import sys
import os
from bson.codec_options import CodecOptions

thisFilePath = os.path.abspath(__file__)
# get the parent folder so to enable the import (this is workaround for not bothering with module structure)
pathToEventStoreAbstract = os.path.dirname(os.path.dirname(thisFilePath))
sys.path.insert(0, pathToEventStoreAbstract)

from eventStoreAbstract import EventStoreAbstract

DEFAULT_DB_NAME = "DEFAULT_DB_EVENT"
DEFAULT_COLLECTION = "EVENT_STORE"

# colors for display of events
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class EventStoreNoSql(EventStoreAbstract):
    
    storeIsSet = False

    def setStore(self, *args, readOnly=False, timeAuto=False, timeZone=None, clientPath=None,
                 db=None, collection=None, regexClassif=None, deletable=False, **kwargs):
        """
        @brief: prepare the store by making the connection. This method should be 
        called before doing any read or write operation on the event store
        @params:
        - readOnly, boolean, if True, the connection is read-only
        - timeAuto, boolean, if True, the time to consider for storing the event is computed in
                           the storeEvent method and no taken from input
        - timeZone, str, the time zone to consider, all times will be converted to UTC in the store 
        - clientPath, str or MongoClient, either the IP for the mongo server, or a pymongo MongoClient object
        - db, str of Database, either the name of the database, or a pymongo Database object
        - collection, str or Collection, either the name of the collection, or a pymongo Collection object
        - regexClassif, function (event) => (str, obj), used to automatically generate
                     a field from the event's content. Typical example is log => log level (if event starts
                     with "ERROR" then level is error)
        - deletable, boolean, if True, the event store can be emptied by the clearAllEvents method
        """

        self.readOnly = readOnly
        self.timeAuto = timeAuto
        self.deletable = deletable
        if clientPath:
            client = MongoClient(clientPath)
        else:
            client = MongoClient('localhost', 27017)
        
        if db:
            if isinstance(db, str):
                dbEvent = client.get_database(db)
            elif isinstance(db, Database):
                dbEvent = db
            else:
                raise TypeError("db is expected to be of type string of pymongo.database.Database")
        else:
            dbEvent = client.get_database(DEFAULT_DB_NAME)
        
        self.dbEvent = dbEvent

        self.timeZone = timeZone
        collectionOptions = {}
        if timeZone:
            collectionOptions['codec_options'] = CodecOptions(tz_aware=True)
        
        if collection:
            if isinstance(collection, str):
                eventCollection = dbEvent.get_collection(collection)
            elif isinstance(collection, Collection):
                if timeZone:
                    print('WARNING: connection to collection was not initiated '\
                          'in eventStore __init__, the time zone option is thus not taken into account')
                eventCollection = collection
            else:
                raise TypeError("collection is expected to be of type string or pymongo.collection.Collection")
        else:
            eventCollection = dbEvent.get_collection(DEFAULT_COLLECTION, **collectionOptions)
        
        self.eventCollection = eventCollection

        self.regexClassif = regexClassif

        self.eventCollection.create_index([('time', ASCENDING)])
        EventStoreNoSql.storeIsSet = True

    def clearAllEvents(self):
        if self.deletable:
            self.eventCollection.drop()
        else:
            raise PermissionError('you are not allowed to drop the event store')

    def storeEvent(self, at=None, event="", **otherFields):
        """
        add an event to the store
        at, datetime or isoformat str, the time of the event
        event, str or anything serilizable in json format
        otherFields, other fields to insert along with the event
        """
        if self.readOnly:
            raise PermissionError('Cannot store new events: read only mode')
        if not self.storeIsSet:
            raise PermissionError("cannot store event before the store is set")
        obj = otherFields
        if not self.timeAuto:
            if not at:
                time = datetime.now()
            elif isinstance(at, str):
                time = self.getDateFromIsoformat(at)
            elif isinstance(at, datetime):
                time = at
            else:
                raise TypeError('at should be of type str or datetime object')
        else:
            # the time was informed but the timeAuto option is set to True
            time = datetime.now()
        
        if self.timeAuto and at:
            print('WARNING: time was provided while option timeAuto was set to True. Will take current time')


        obj['time'] = time
        obj['event'] = event
        
        if self.regexClassif:
            key, val = self.regexClassif(event)
            obj[key] = val

        self.eventCollection.insert_one(obj)

    def getEvents(self, fromTime=None, toTime=None, otherQueries=[], inListForm=False,
                  orderBy=None, ascending=True):
        """
        retrieve events from store
        from, datetime or isofrmat str,
        to, datetime or isoformat str,
        otherQuery, list of mongodb query-like dictionnaries to add to the query
        inListForm, boolean, if True returns a list and not a cursor (= generator)
        orderBy, str, the field to sort results on
        ascending, boolean, if True then sorts in ascending order, else descending order
        """
        if not self.storeIsSet:
            raise PermissionError("cannot store event before the store is set")
        queryObj = otherQueries
            
        if fromTime:
            if isinstance(fromTime, str):
                fromTime = self.getDateFromIsoformat(fromTime)
            queryObj.append({'time' : {'$gte' : fromTime}})
        if toTime:
            if isinstance(toTime, str):
                toTime = self.getDateFromIsoFormat(toTime)
            queryObj.append({'time' : {'$lte' : toTime}})
        if len(queryObj) > 0:
            query = {"$and" : queryObj}
        else:
            query = {}
        res = self.eventCollection.find(query)
        if orderBy:
            order = ASCENDING if ascending else DESCENDING
            res = res.sort(orderBy, order)

        res = self.rmIdNext(res)

        if inListForm:
            resList = []
            while True:
                try:
                    evt = res.__next__()
                    resList.append(evt)
                except StopIteration:
                    break

            res = resList
        return res

    @staticmethod
    def rmIdNext(resCursor):
        resCursor.__origNext__ = resCursor.__next__

        # class overriding the dict class in results
        class prettyDict:
            def __str__(slf):
                printSt = bcolors.HEADER + bcolors.OKBLUE + slf['time'].isoformat() + bcolors.ENDC + " "
                for elem in slf:
                    if elem != "time":
                        if elem == 'event':
                            printSt += elem + ': '+ bcolors.UNDERLINE + str(slf[elem]) + bcolors.ENDC + "  "
                        else:
                            printSt +=  elem + ': ' + str(slf[elem]) + " ; "
                return printSt
            
            def __repr__(slf):
                reprStr = bcolors.HEADER + bcolors.OKBLUE + slf['time'].isoformat() + bcolors.ENDC + "  "
                for elem in slf:
                    if elem != "time":
                        if elem == 'event':
                            reprStr += elem + ': '+ bcolors.UNDERLINE + str(slf[elem]) + bcolors.ENDC + "  "
                        else:
                            reprStr +=  elem + ': ' + str(slf[elem]) + " ; "
                return reprStr

        # class overriding the dict class in results
        class newStrDict(prettyDict, dict):
            pass

        def newNext(slf):
            def nnext():
                nxt = slf.__origNext__()
                del nxt['_id']
                nxt = newStrDict(nxt)
                #nxt.__str__
                return nxt
            return nnext
        resCursor.__next__ = newNext(resCursor)
        resCursor.next = resCursor.__next__

        return resCursor

    @staticmethod
    def getDateFromIsoformat(dt):
        try:
            time = datetime.fromisoformat(dt)
        except ValueError:
            raise ValueError('at was not recognized as datetime, either use the datetime.datetime class, or an isoformat string')
        return time

