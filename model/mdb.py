from pymongo import MongoClient
from math import ceil
import json

class getdata(object):

    def __init__(self, collection, query=None, per_page=10, page=1):

        self.query = query
        self.per_page = per_page
        self.page = int(page)
        self.collection = collection
        self.get_data()



    def get_data(self):
        con = MongoClient()
        db = con.songs
        col = db[self.collection]

        self._min = 0 if self.page == 1 else (self.page - 1)*self.per_page
        self._max = self.page * self.per_page

        self.data = col.find(self.query)[self._min:self._max]
        self.total_documents = self.data.count()
        self.total_pages =  int(ceil(self.total_documents / float(self.per_page)))
        self.has_next = self.page < self.total_pages
        self.has_previous = self.page > 1





    def __iter__(self, page=False):
        if page:
            self.page = page
            self.get_data()

        for item in self.data:
            yield item


class document(object):

    def __init__(self, collection=None):
        self.collection = collection

    def save(self):
        _dbo = {}
        for key,value in self.__dict__.items():
            if type(value) is field:
                _dbo[key] = value.value
        js = json.dumps(_dbo)
        con = MongoClient()
        db = con.songs
        col = db[self.collection]
        idx = col.insert(_dbo)
        print(idx)





class field(object):

    def __init__(self, required=False, length=150, value=None):
        self.length = length
        self.required = required
        self.value = value



class artist(document):
    def __init__(self):
        self.collection = "artist"
        albumartist = field()

class album(document):

    def __init__(self):
        self.collection = "album"
        albumtitle = field()
        albumartist = field()

class song(document):

    def __init__(self):
        self.collection = "song"
        self.songtitle = field()
        self.albumartist = field()
        self.album = field()
        self.tracknumber = field()
        self.artist = field()
        self.filepath = field()



