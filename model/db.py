from mutagenx.easyid3 import EasyID3, EasyID3KeyError
import os
from mongoengine import *
from math import ceil


class artist(Document):
    id = UUIDField()
    albumartist = StringField(required=False, unique=True)
    musicbrainz_artistid = StringField()
    musicbrainz_albumartistid = StringField()

class album(Document):
    id = UUIDField()
    albumtitle = StringField(required=False, unique=True)
    albumartist = ReferenceField(artist)
    musicbrainz_albumartistid = StringField()
    musicbrainz_albumid = StringField()

class song(Document):
    id = UUIDField()
    songtitle = StringField(required=False, unique_with=('albumartist','album','tracknumber'))
    albumartist = ReferenceField(artist)
    album = ReferenceField(album)
    tracknumber = StringField(required=False)
    artist = StringField(required=False)
    musicbrainz_trackid = StringField()
    filepath = StringField(required=False)


class paginate():

    def __init__(self, current_page=1, per_page=10):
        self.current_page = int(current_page)
        self.per_page = per_page
        self.min = 0 if self.current_page == 1 else (self.current_page - 1)*self.per_page
        self.max = self.current_page * self.per_page

    @property
    def total_documents(self):
        return self._total_documents


    @total_documents.setter
    def total_documents(self, value):
        self._total_documents = value
        self.total_pages = int(ceil(self._total_documents / float(self.per_page)))
        self.has_next = self.current_page < self.total_pages
        self.has_previous = self.current_page > 1






def mp3_files(path):
    for root, subFolders, files in os.walk(path, topdown=False):
        for f in files:
            if f.endswith("mp3"):
                yield os.path.join(root, f)

def add_collection(path, update=False):

    connect('newsongs', host='127.0.0.1', port=27017)

    id3_template = ['performer',                   #maps to: albumartist
                 'album',                       #maps to: albumtitle
                 'title',                       #maps to: songtitle
                 'tracknumber',                 #maps to: same
                 'artist',                      #maps to:
                 'musicbrainz_albumartistid',   #maps to: same
                 'musicbrainz_albumid',         #maps to: same
                 'musicbrainz_artistid',        #maps to: same
                 'musicbrainz_releasegroupid',  #maps to: same
                 'musicbrainz_trackid',         #maps to: same
                 'totaltracks',                 #maps to: same
                ]

    for file in mp3_files(path):


        id3_file = EasyID3(file)
        id3_info = []

        for item in id3_template:
            id3_info.append(get_id3_item(item, id3_file))

        id3 = dict(zip(id3_template,id3_info))


        if artist.objects(albumartist=id3['performer']).first() == None:
            _artist = artist()
        else:
            _artist = artist.objects(albumartist=id3['performer']).first()

        _artist.albumartist = id3['performer']
        _artist.musicbrainz_artistid = id3['musicbrainz_artistid']
        _artist.save()


        if album.objects(albumtitle=id3['album']).first() == None:
            _album = album()
        else:
            _album = album.objects(albumtitle=id3['album']).first()

        _album.albumtitle = id3['album']
        _album.musicbrainz_albumid = id3['musicbrainz_albumid']
        _album.musicbrainz_albumartistid = id3['musicbrainz_albumartistid']
        _album.albumartist = _artist
        _album.save()



        if song.objects(songtitle=id3['title'], albumartist=_artist, album=_album).first() == None:
            _song = song()
        else:
            _song = song.objects(songtitle=id3['title'], albumartist=_artist, album=_album).first()

        _song.songtitle=id3['title']
        _song.albumartist = _artist
        _song.album = _album
        _song.artist = id3['artist']
        _song.tracknumber = id3['tracknumber']
        _song.musicbrainz_trackid = id3['musicbrainz_trackid']
        _song.filepath = file
        _song.save()




def get_id3_item(item, id3):
    try:
        val = id3[item][0]
    except EasyID3KeyError:
        val = None
    except Exception as e:
        pass

    return val

# def db_get(query):
#     connect('songs', host='127.0.0.1', port=27017)
#     itemfrom, itemto = pagerange(int(query["page"]["current"]), int(query["page"]["pagesize"]))
#
#     if query["collection"] == "artist":
#         collection = artist
#         if query["where"] != "None":
#             data = collection.objects(albumartist__icontains=query["where"])
#         else:
#             data = collection.objects[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects())
#     elif query["collection"] == "album":
#         collection = album
#         if query["where"] != "None":
#             data = collection.objects(albumtitle__icontains=query["where"])[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects(albumtitle__icontains=query["where"]))
#         elif id:
#             data = collection.objects(albumartist=query["id"])[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects(albumartist=query["id"]))
#         else:
#             data = collection.objects[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects())
#
#     elif query["collection"] == "song":
#
#         collection = song
#         if query["where"] != "None":
#             data = collection.objects(songtitle__icontains=query["where"])[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects(songtitle__icontains=query["where"]))
#         elif query["album_id"]:
#             data = collection.objects(album=query["album_id"])[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects(album=query["id"]))
#         elif query["song_id"]:
#             data = collection.objects(id=query["song_id"])
#             query["page"]["totaldocuments"] = len(collection.objects(id=query["id"]))
#         else:
#             data = collection.objects[itemfrom:itemto]
#             query["page"]["totaldocuments"] = len(collection.objects())
#
#
#     query = pageobj(query, collection)
#     return data,query


# def pageobj(query, collection):
#     connect('songs', host='127.0.0.1', port=27017)
#
#     query["page"]["totalpages"] = math.ceil(query["page"]["totaldocuments"]/query["page"]["pagesize"])
#     query["page"]["next"] = query["page"]["current"] + 1 if query["page"]["current"] < query["page"]["totalpages"] else 0
#     query["page"]["previous"] = query["page"]["current"] - 1 if query["page"]["current"] != 1 else 0
#     #_pages = {x:'Page %s' % (x) for x in range(1,_totalpages)}
#     return query
#
#
# def pagerange(page, pagesize):
#     max = page * pagesize
#     if page == 1:
#         min = 0
#     else:
#         min = (page - 1)*pagesize
#
#     return min,max