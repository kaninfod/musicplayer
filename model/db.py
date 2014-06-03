from mutagenx.easyid3 import EasyID3
import os
from mongoengine import *

import json
import math
import re


class artist(Document):
    id = UUIDField()
    albumartist = StringField(required=False, unique=True)

class album(Document):
    id = UUIDField()
    albumtitle = StringField(required=False, unique=True)
    albumartist = ReferenceField(artist)

class song(Document):
    id = UUIDField()
    songtitle = StringField(required=False, unique_with=('albumartist','album','tracknumber'))
    albumartist = ReferenceField(artist)
    album = ReferenceField(album)
    tracknumber = StringField(required=False)
    artist = StringField(required=False)
    filepath = StringField(required=False)




def mp3_files(path):
    for root, subFolders, files in os.walk(path, topdown=False):
        for f in files:
            if f.endswith("mp3"):
                yield os.path.join(root, f)

def add_collection(path, update=False):

    connect('songs', host='127.0.0.1', port=27017)
    for file in mp3_files(path):
        id3 = EasyID3(file)
        try:
            try:
                _artist = artist.objects.get(albumartist=id3['performer'][0])
            except DoesNotExist:
                _artist = artist()
                _artist.albumartist = id3['performer'][0]
                _artist.save()

            try:
                _album = album.objects.get(albumtitle=id3['album'][0])
            except DoesNotExist:
                _album = album()
                _album.albumtitle = id3['album'][0]
                _album.albumartist = _artist
                _album.save()

            try:
                _song = song.objects.get(songtitle=id3['title'][0], albumartist=_artist, album=_album)
            except DoesNotExist:
                _song = song()
                _song.songtitle=id3['title'][0]
                _song.albumartist = _artist
                _song.album = _album
                _song.artist = id3['artist'][0]
                _song.tracknumber = id3['tracknumber'][0]
                _song.filepath = file
                _song.save()
        except Exception as e:
            print(e, file)

def db_get(query):
    connect('songs', host='127.0.0.1', port=27017)
    itemfrom, itemto = pagerange(int(query["page"]["current"]), int(query["page"]["pagesize"]))

    if query["collection"] == "artist":
        collection = artist
        if query["where"] != "None":
            data = collection.objects(albumartist__icontains=query["where"])
        else:
            data = collection.objects[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects())
    elif query["collection"] == "album":
        collection = album
        if query["where"] != "None":
            data = collection.objects(albumtitle__icontains=query["where"])[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects(albumtitle__icontains=query["where"]))
        elif id:
            data = collection.objects(albumartist=query["id"])[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects(albumartist=query["id"]))
        else:
            data = collection.objects[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects())

    elif query["collection"] == "song":

        collection = song
        if query["where"] != "None":
            data = collection.objects(songtitle__icontains=query["where"])[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects(songtitle__icontains=query["where"]))
        elif query["album_id"]:
            data = collection.objects(album=query["album_id"])[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects(album=query["id"]))
        elif query["song_id"]:
            data = collection.objects(id=query["song_id"])
            query["page"]["totaldocuments"] = len(collection.objects(id=query["id"]))
        else:
            data = collection.objects[itemfrom:itemto]
            query["page"]["totaldocuments"] = len(collection.objects()) 


    query = pageobj(query, collection)
    return data,query


def pageobj(query, collection):
    connect('songs', host='127.0.0.1', port=27017)

    query["page"]["totalpages"] = math.ceil(query["page"]["totaldocuments"]/query["page"]["pagesize"])
    query["page"]["next"] = query["page"]["current"] + 1 if query["page"]["current"] < query["page"]["totalpages"] else 0
    query["page"]["previous"] = query["page"]["current"] - 1 if query["page"]["current"] != 1 else 0
    #_pages = {x:'Page %s' % (x) for x in range(1,_totalpages)}
    return query


def pagerange(page, pagesize):
    max = page * pagesize
    if page == 1:
        min = 0
    else:
        min = (page - 1)*pagesize

    return min,max

