from mutagenx.easyid3 import EasyID3, EasyID3KeyError
import musicbrainzngs
import os
from app import db
from app import cache
from math import ceil
import time
import urllib
import PIL



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
    coverimage = db.ImageField()

    def get_coverart_url(self):
        path = "app/static/media/"
        filename = "%s.jpg" % self.id

        if not self.coverimage.size:
            raise NameError("No image in DB")
        imgdata = self.coverimage.read()
        if not imgdata:
            raise NameError("No image in DB")
        b_imagedata = bytes(imgdata)
        output = open("%s%s" % (path, filename), "wb")
        output.write(b_imagedata)
        return filename


class song(db.Document):
    id = db.UUIDField()
    songtitle = db.StringField(required=False, unique_with=('albumartist','album','tracknumber'))
    albumartist = db.ReferenceField(artist)
    album = db.ReferenceField(album)
    tracknumber = db.IntField(required=False)
    artist = db.StringField(required=False)
    musicbrainz_trackid = db.StringField()
    filepath = db.StringField(required=False)

class mp3_file(object):

    def __init__(self, file, update=False):
        _id3 = self.id3(file)

        if (_id3.performer == None or _id3.album == None or _id3.title == None):
            return

        self.artist = self.add_update_artist(_id3)
        _id3.performer = self.artist
        self.album = self.add_update_album(_id3)
        _id3.album = self.album
        self.song = self.add_update_song(_id3)



    def add_update_artist(self, id3):

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
        self.get_coverart(self.album)

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
        l = id3.tracknumber.split("/")

        if len(l) > 0:
            self.song.tracknumber = l[0]
        else:
            self.song.tracknumber = id3.tracknumber
        self.song.musicbrainz_trackid = id3.musicbrainz_trackid
        self.song.filepath = id3.filepath
        self.song.save()
        return self.song

    def get_coverart(self, album):
        path = "app/static/media/"
        filename = "%s.jpg" % album.id

        musicbrainzngs.set_useragent("python-musicplayer-flask","0.1","martinhinge@gmail.com")
        covers = cache.get('covers')
        if album.id in covers:
            return

        covers.append(album.id)
        cache.set("covers", covers)


        if not album.musicbrainz_albumid or album.coverimage:
            return
            #raise NameError('musicbrainz_albumid not set')
        try:
            data = musicbrainzngs.get_image_list(album.musicbrainz_albumid)
        except Exception as e:
            return e

        if len(data['images']) == 0:
            raise NameError('No images returned from service')

        urllib.request.urlretrieve(data['images'][0]['image'], "%s%s" % (path, filename))
        ci = open("%s%s" % (path, filename), 'rb')
        album.coverimage.put(ci, content_type = 'image/jpeg')


        return


    class id3(object):
        def __init__(self, mp3_file):
            id3 = ['performer',
                   'album',
                   'title',
                   'tracknumber',
                   'artist',
                   'musicbrainz_albumartistid',
                   'musicbrainz_albumid',
                   'musicbrainz_artistid',
                   'musicbrainz_releasegroupid',
                   'musicbrainz_trackid',
                   'totaltracks']

            mb_artist = ['country',
                         'type']

            mb_release = ['barcode',
                          'country',
                          'date']


            id3_file = EasyID3(mp3_file)

            for item in id3:
                self.__dict__[item] = self.get_id3_item(item,id3_file)
            self.filepath = mp3_file

        def get_id3_item(self, item, id3):
            try:
                val = id3[item][0]
            except Exception as e:
                val = None

            return val

def add_collection(path):

    covers = []
    cache.set("covers", covers)
    for file in mp3_files(path):
        try:
            mp3_obj = mp3_file(file)
            #print("%s    %s   -   %s" % (time.strftime("%I:%M:%S"), mp3_obj.song.songtitle, mp3_obj.artist.albumartist))
        except Exception as e:
            print(e)
            print("Something's up with this file %s" % file)


def mp3_files(path):
    for root, subFolders, files in os.walk(path, topdown=False):
        for f in files:
            if f.endswith("mp3"):
                yield os.path.join(root, f)


class musicbrainz(object):

    def __init__(self, album):
        self.album = album
        self.path = "app/static/media/"
        self.filename = "%s.jpg" % self.album.id

    def get_coverart(self):

        musicbrainzngs.set_useragent("python-musicplayer-flask","0.1","martinhinge@gmail.com")
        if not self.album.musicbrainz_albumid:
            raise NameError('musicbrainz_albumid not set')

        try:
            data = musicbrainzngs.get_image_list(self.album.musicbrainz_albumid)
        except Exception as e:
            return e

        if data['images'].len == 0:
            raise NameError('No images returned from service')

        urllib.request.urlretrieve(data['images'][0]['image'], "%s%s" % (self.path, self.filename))
        ci = open("%s%s" % (self.path, self.filename), 'rb')
        self.album.coverimage.put(ci, content_type = 'image/jpeg')
        self.album.save()

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
