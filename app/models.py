from mutagenx.easyid3 import EasyID3, EasyID3KeyError
import os
from app import db
from math import ceil
import time



class artist(db.Document):
    id = db.UUIDField()
    albumartist = db.StringField(required=False, unique=True)
    musicbrainz_artistid = db.StringField()
    musicbrainz_albumartistid = db.StringField()

class album(db.Document):
    id = db.UUIDField()
    albumtitle = db.StringField(required=False, unique=True)
    albumartist = db.ReferenceField(artist)
    musicbrainz_albumartistid = db.StringField()
    musicbrainz_albumid = db.StringField()

class song(db.Document):
    id = db.UUIDField()
    songtitle = db.StringField(required=False, unique_with=('albumartist','album','tracknumber'))
    albumartist = db.ReferenceField(artist)
    album = db.ReferenceField(album)
    tracknumber = db.StringField(required=False)
    artist = db.StringField(required=False)
    musicbrainz_trackid = db.StringField()
    filepath = db.StringField(required=False)







def add_collection(path):
    for file in mp3_files(path):
        add_file_to_db(file)


def mp3_files(path):
    for root, subFolders, files in os.walk(path, topdown=False):
        for f in files:
            if f.endswith("mp3"):
                yield os.path.join(root, f)


class mp3_file(object):
    def __init__(self, file, update=False):


def add_file_to_db(file, update=False):

    _id3 = id3(file)

    _artist = add_update_artist(_id3)
    _id3.performer = _artist
    _album = add_update_album(_id3)
    _id3.album = _album
    _song = add_update_song(_id3)

    print("%s    %s   -   %s" % (time.strftime("%I:%M:%S"),_id3.title, _id3.performer))

def add_update_artist(id3):

    if (id3.performer == None or id3.album == None or id3.title == None):
        return

    if artist.objects(albumartist=id3.performer).first() == None:
        _artist = artist()
    else:
        _artist = artist.objects(albumartist=id3.performer).first()

    _artist.albumartist = id3.performer
    _artist.musicbrainz_artistid = id3.musicbrainz_artistid
    _artist.save()
    return _artist

def add_update_album(id3):
    if album.objects(albumtitle=id3.album).first() == None:
        _album = album()
    else:
        _album = album.objects(albumtitle=id3.album).first()

    _album.albumtitle = id3.album
    _album.musicbrainz_albumid = id3.musicbrainz_albumid
    _album.musicbrainz_albumartistid = id3.musicbrainz_albumartistid
    _album.albumartist = id3.performer
    _album.save()
    return _album

def add_update_song(id3):
    if song.objects(songtitle=id3.title, albumartist=id3.performer, album=id3.album).first() == None:
        _song = song()
    else:
        _song = song.objects(songtitle=id3.title, albumartist=id3.performer, album=id3.album).first()

    _song.songtitle=id3.title
    _song.albumartist = id3.performer
    _song.album = id3.album
    _song.artist = id3.artist
    _song.tracknumber = id3.tracknumber
    _song.musicbrainz_trackid = id3.musicbrainz_trackid
    _song.filepath = id3.filepath
    _song.save()
    return _song


class id3(object):

    def __init__(self, mp3_file):
        self.performer = None                    #maps to: albumartist
        self.album = None                      #maps to: albumtitle
        self.title = None                      #maps to: songtitle
        self.tracknumber = None                #maps to: same
        self.artist = None                     #maps to:
        self.musicbrainz_albumartistid = None  #maps to: same
        self.musicbrainz_albumid = None        #maps to: same
        self.musicbrainz_artistid = None       #maps to: same
        self.musicbrainz_releasegroupid = None #maps to: same
        self.musicbrainz_trackid = None        #maps to: same
        self.totaltracks = None                #maps to: same
        self.filepath = mp3_file


        id3_file = EasyID3(mp3_file)

        for item in self.__dict__:
            self.__dict__[item] = self.get_id3_item(item,id3_file)


    def get_id3_item(self, item, id3):
        try:
            val = id3[item][0]
        except Exception as e:
            val = None

        return val

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
