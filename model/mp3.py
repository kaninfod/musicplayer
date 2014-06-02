from builtins import print
from mutagenx.easyid3 import EasyID3
import os
import uuid

from .artists import artists, artist
from .albums import albums, album
from .songs import songs, song
from .data import *

ENTRY_POINT = "http://127.0.0.1:5000"



class music:
    def __init__(self, name):
        self.name = name
        self.artists = artists()
        self.songs = songs()
        self.albums = albums()
        self.api = api()
        self.resources = resources()


    def __get_artists(self):
        artists = self.api.api_get(self.resources.artists())
        for item in artists:
            self.artists[artist(item).id] = artist(item)


    def __get_albums(self):
        albums = self.api.api_get(self.resources.albums())
        for item in albums:
            self.albums[album(item).id] = album(item)

    def __get_songs(self):
        songs = self.api.api_get(self.resources.songs())
        for item in songs:
            s = song(item)
            s.artist = self.artists[s.artist]
            s.album = self.albums[s.album]
            self.songs[s.id] = s


    def mp3_files(self, path):
        for root, subFolders, files in os.walk(path, topdown=False):
            for f in files:
                if f.endswith("mp3"):
                    yield os.path.join(root, f)




    def add_collection(self, path, update=False):

        for file in self.mp3_files(path):
            try:
                id3 = EasyID3(file)
                #print(id3['performer'][0],id3['artist'][0], id3['album'][0], id3['title'][0])
                #print(id3['albumartist'][0])


                artist_id = self.__db_commit_artist({
                    'name': id3['performer'][0]
                })

                album_id = self.__db_commit_album(update, {
                    'name': id3['album'][0],
                    'artist': artist_id,
                })

                song_id = self.__db_commit_song(update, {
                        'title': id3['title'][0],
                        'artist': artist_id,
                        'album': album_id,
                        'tracknumber': id3['tracknumber'][0],

                    })
                #print('ok')
            except:
                print("This was not loaded: " + file)

    def __db_commit_artist(self, args):
        qry = self.api.api_get(resource=self.resources.artists(), where={"name": args['name']})
        if len(qry['_items']) == 0:
            #data = {'name': args['name']}
            qry = self.api.api_post(self.resources.artists(), args)
            return qry['_id']
        else:
            return qry['_items'][0]['_id']

    def __db_commit_album(self, update, args):
        qry = self.api.api_get(
            resource=self.resources.albums(),
            where={"name": args['name']}
        )
        if len(qry['_items']) == 0:
            qry = self.api.api_post(resource=self.resources.albums(), data=args)
            return qry['_id']
        else:
            if update:
                upd = self.api.api_update(resource=self.resources.albums(qry['_items'][0]['_id']), etag=qry['_items'][0]['_etag'], data=args)
            return qry['_items'][0]['_id']


    def __db_commit_song(self, update, args):
        qry = self.api.api_get(
            resource=self.resources.songs(),
            where={
                "title": args['title'],
                "artist": args['artist']
            }
        )
        if len(qry['_items']) == 0:
            qry = self.api.api_post(resource=self.resources.songs(), data=args)
            return qry['_id']
        else:
            if update:
                upd = self.api.api_update(resource=self.resources.songs(qry['_items'][0]['_id']), etag=qry['_items'][0]['_etag'], data=args)
            return qry['_items'][0]['_id']
