from    model.db import add_collection, db_get
from flask import Flask, render_template, request,session
#import model.data
from model.db import *
import os
import model.mgo
from bson import ObjectId
from bson.json_util import dumps

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
def artists():
    return render_template('artists.html')

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

    data, query = db_get(query=query)
    session["artist"] =  query

    return render_template('artistsList.html', data=data, query=query)


@app.route('/albums')
@app.route('/albums/<id>')
def albums(id = ""):
    return render_template('albums.html', artistid=id)

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
    if "song" in session:
        query = session["song"]
        query["album_id"] = False
    else:
        query = {
            "collection":"song",
            "page":{
                "current":1,
                "pagesize":10
            },
            "where":"None",
            "song_id":False
        }

    query["song_id"] = song_id

    data, page = db_get(query=query)
    data = model.mgo.clssong(collection="song",query={'_id':ObjectId(song_id)})
    mediapath = "/home/martin/python/musicplayer/static/media/"
    songlink = "%s.mp3" % (data[0].id)
    songpath = mediapath + songlink
    try:
        os.symlink(data[0].filepath, songpath)
    except FileExistsError:
        os.remove(songpath)
        os.symlink(data[0].filepath, songpath)


    return render_template('songplay.html',
                        title = data[0].songtitle, song=songlink)

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
    k = model.mgo.clssong(collection='song')
    for i in k:
        print(i)


    if k.has_next():
        k.page = k.page +1

    for i in k.__iter__(page=3):
        print(i)




SERVER_NAME = "127.0.0.1"
SERVER_PORT = 5001

if __name__ == '__main__':
    app.run(SERVER_NAME, SERVER_PORT, debug=False, threaded=True)
