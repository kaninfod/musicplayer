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

class mp3_file(object):
    def __init__(self, file, update=False):

        _id3 = self.id3(file)
    
        self.artist = self.add_update_artist(_id3)
        _id3.performer = self.artist
        self.album = self.add_update_album(_id3)
        _id3.album = self.album
        self.song = self.add_update_song(_id3)
    


    def add_update_artist(self, id3):
    
        if (id3.performer == None or id3.album == None or id3.title == None):
            return
    
        if artist.objects(albumartist=id3.performer).first() == None:
            self.artist = artist()
        else:
            self.artist = artist.objects(albumartist=id3.performer).first()
    
        self.artist.albumartist = id3.performer
        self.artist.musicbrainz_artistid = id3.musicbrainz_artistid
        self.artist.save()
        return self.artist
    
    def add_update_album(self, id3):
        if album.objects(albumtitle=id3.album).first() == None:
            self.album = album()
        else:
            self.album = album.objects(albumtitle=id3.album).first()
    
        self.album.albumtitle = id3.album
        self.album.musicbrainz_albumid = id3.musicbrainz_albumid
        self.album.musicbrainz_albumartistid = id3.musicbrainz_albumartistid
        self.album.albumartist = id3.performer
        self.album.save()
        return self.album
    
    def add_update_song(self, id3):
        if song.objects(songtitle=id3.title, albumartist=id3.performer, album=id3.album).first() == None:
            self.song = song()
        else:
            self.song = song.objects(songtitle=id3.title, albumartist=id3.performer, album=id3.album).first()
    
        self.song.songtitle=id3.title
        self.song.albumartist = id3.performer
        self.song.album = id3.album
        self.song.artist = id3.artist
        self.song.tracknumber = id3.tracknumber
        self.song.musicbrainz_trackid = id3.musicbrainz_trackid
        self.song.filepath = id3.filepath
        self.song.save()
        return self.song


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



def add_collection(path):
    for file in mp3_files(path):
        mp3_obj = mp3_file(file)
        print("%s    %s   -   %s" % (time.strftime("%I:%M:%S"), mp3_obj.song.songtitle, mp3_obj.artist.albumartist))

def mp3_files(path):
    for root, subFolders, files in os.walk(path, topdown=False):
        for f in files:
            if f.endswith("mp3"):
                yield os.path.join(root, f)
