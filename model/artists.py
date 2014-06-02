class artists:
    def __init__(self):
        self.__items = {}


    def __getitem__(self, item):
        return self.__items[item]

    def __setitem__(self, key, value):
        self.__items[key] = value

    def __iter__(self):
        return self.__items.itervalues()


class artist:
    def __init__(self, db_json):
        self.id = db_json['_id']
        self.name = db_json['name']
        self.musicbrainz_artistid = ''


    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
