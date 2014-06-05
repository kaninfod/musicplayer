from pymongo import MongoClient
from math import ceil

class clssong(object):

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
