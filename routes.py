import re
import os

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from bson import ObjectId
from bson.json_util import dumps

from model.db import *
from model.db import add_collection
from model.db import db_get

from model.mdb import getdata


app = Flask(__name__)
app.secret_key = 'development key'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/songs')
@app.route('/songs/<albumid>')
def songs(albumid = ""):
    return render_template('songs.html', albumid=albumid)

@app.route('/songsList', methods=['GET', 'POST'] )
def songsList(id=""):
    if "song" in session:
        query = session["song"]
    else:
        query = {
            "collection":"song",
            "page":{
                "current":1,
                "pagesize":10
            },
            "where":"None",
            "id":""
        }

    query['page']['current'] = int(request.args.get("page", query['page']['current']))
    query["where"] = request.args.get("where", query['where'])
    query["album_id"] = request.args.get("album_id",query['id'])

    data, query = db_get(query=query)
    session["song"] = query

    return render_template('songsList.html', data=data, query=query)

@app.route('/artists')
@app.route('/artists/page/<page>')
def artists(page=1):
    qstr = (request.args.get("q"))

    if qstr:
        query = {'albumartist':{'$regex':'%s' % (qstr),'$options': '-i'}}
    else:
        query = None
        qstr = ""

    page =int(page)
    data = getdata(collection="artist", page=page, query=query)

    return render_template('artists.html', data=data, page=page, q=qstr)

@app.route('/artistsList', methods=['GET', 'POST'] )
def artistsList():
    if  "artist" in session:
        query = session["artist"]
    else:
        query = {
            "collection":"artist",
            "page":{
                "current":1,
                "pagesize":10
            },
            "where":"None"
        }


    query["page"]["current"] = int(request.args.get("page", query['page']['current']))
    query["where"] = request.args.get("where", query['where'])

    page = int(request.args.get("page", 1))
    data, query = db_get(query=query)
    q = {'artist':request.args.get("where")}
    data = model.mdb.clssong(collection="artist", page=page, query=q)
    session["artist"] =  query

    return render_template('artistsList.html', data=data, query=query)


@app.route('/albums')
@app.route('/albums/<id>') # to go
@app.route('/albums/artist/<artist_id>/page/<page>')
@app.route('/albums/page/<page>')
def albums(page=1, artist_id=None):
    qstr = (request.args.get("q",""))

    if qstr:
        query = {'albumtitle':{'$regex':'%s' % (qstr),'$options': '-i'}}
    elif artist_id:
        query = {'albumartist':ObjectId(artist_id)}
    else:
        query = None

    page =int(page)
    data = getdata(collection="album", page=page, query=query)

    return render_template('albums.html', data=data, page=page, q=qstr)


def url_for_other_page(**kwargs):
    args = request.view_args.copy()
    for key, value in kwargs.items():
        #if args[key]:
            args[key] = value
    return url_for(request.endpoint, **args)






@app.route('/albumsList')
def albumsList():
    if "album" in session:
        query = session["album"]
    else:
        query = {
            "collection":"album",
            "page":{
                "current":1,
                "pagesize":10
            },
            "where":"None",
            "id":False
        }

    query['page']['current'] = int(request.args.get("page", query['page']['current']))
    query["where"] = request.args.get("where", query['where'])
    query["id"] = request.args.get("id",query['id'])

    data, query = db_get(query=query)
    session["album"]= query

    return render_template('albumsList.html', data=data, query=query)

@app.route('/playsong/<song_id>')
def playsong(song_id):
    # if "song" in session:
    #     query = session["song"]
    #     query["album_id"] = False
    # else:
    #     query = {
    #         "collection":"song",
    #         "page":{
    #             "current":1,
    #             "pagesize":10
    #         },
    #         "where":"None",
    #         "song_id":False
    #     }
    #
    # query["song_id"] = song_id

    #response, page = db_get(query=query)
    response = model.mdb.clssong(collection="song",query={'_id':ObjectId(song_id)})
    song_object = response.data[0]
    mediapath = "/home/martin/python/musicplayer/static/media/"
    songlink = "%s.mp3" % (song_object['_id'])
    songpath = mediapath + songlink

    filepath = song_object['filepath']
    try:
        os.symlink(filepath, songpath)
    except FileExistsError:
        os.remove(songpath)
        os.symlink(filepath, songpath)


    return render_template('songplay.html',
                        title = song_object['songtitle'], song=songlink)

    #test

@app.route('/updatedb')
def updatedb():
    m = music('kaj')
    #m.add_collection("/home/martin/Downloads/music", True)
    #m.add_collection("/media/store/Music")
    add_collection("/media/store/Music")
    #k=dbGet()
    #print("done")

@app.route('/sg')
def test():
    q = {"album":ObjectId("53847b86936aa27d64003c9f")}
    k = model.mdb.clssong(collection='song')
    for i in k:
        print(i)


    if k.has_next():
        k.page = k.page +1

    for i in k.__iter__(page=3):
        print(i)





SERVER_NAME = "127.0.0.1"
SERVER_PORT = 5001
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

if __name__ == '__main__':
    app.run(SERVER_NAME, SERVER_PORT, debug=False, threaded=True)


