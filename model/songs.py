class songs():
    def __init__(self):
        self.__items = {}


    def __getitem__(self, item):
        return self.__items[item]


    def __setitem__(self, key, value):
        self.__items[key] = value

    def __iter__(self):
        return self.__items.itervalues()


class song:
    def __init__(self, db_json):
        self.id = db_json['_id']
        self.title = db_json['title']
        self.artist = db_json['artist']
        self.album = db_json['album']
        self.tracknumber = db_json['tracknumber']
        #self.length = db_json['length']

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
