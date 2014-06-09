


from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from bson import ObjectId
from bson.json_util import dumps

import model.db
from model.db import *
from model.db import add_collection
from model.db import db_get

from model.mdb import *


app = Flask(__name__)
app.secret_key = 'development key'


@app.route('/')
def home():
    return render_template('home.html')

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



@app.route('/albums')
@app.route('/albums/artist/<artist_id>/page/<page>')
@app.route('/albums/artist/<artist_id>')
@app.route('/albums/page/<page>')
def albums(page=1, artist_id=None):

    connect('songs', host='127.0.0.1', port=27017)
    p = paginate(page,10)
    qstr = (request.args.get("q",""))


    if qstr:
        data = model.db.album.objects(albumtitle__icontains=qstr)
    elif artist_id:
        data = model.db.album.objects(albumartist=artist_id)

    p.total_documents = data.count()
    data = data[p.min:p.max]

    return render_template('albums.html', data=data, paginate=p, q=qstr)

@app.route('/songs')
@app.route('/songs/album/<album_id>/page/<page>')
@app.route('/songs/album/<album_id>')
@app.route('/songs/page/<page>')
def songs(page=1, album_id=""):
    qstr = (request.args.get("q",""))

    if qstr:
        query = {'songtitle':{'$regex':'%s' % (qstr),'$options': '-i'}}
    elif album_id:
        query = {'album':ObjectId(album_id)}
    else:
        query = None

    page =int(page)
    data = getdata(collection="song", page=page, query=query)

    return render_template('songs.html', data=data, page=page, q=qstr)

def url_for_other_page(**kwargs):
    args = request.view_args.copy()
    for key, value in kwargs.items():
        #if args[key]:
            args[key] = value
    return url_for(request.endpoint, **args)

@app.route('/playsong', methods=['GET', 'POST'])
def playsong():
    song_id = (request.args.get("song_id",""))

    response = getdata(collection="song",query={'_id':ObjectId(song_id)})
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


    return render_template('songplay.html', title = song_object['songtitle'], song=songlink)


@app.route('/updatedb')
def updatedb():
    #m = music('kaj')
    #m.add_collection("/home/martin/Downloads/music", True)
    #m.add_collection("/media/store/Music")
    add_collection("/media/store/Music")
    #k=dbGet()
    #print("done")

@app.route('/slugify/<s>')
def slugify(s):
    num_chars = 25
    # remove all these words from the string before urlifying
    #s = downcode(s)
    removelist = ['a', 'an', 'as', 'at', 'before', 'but', 'by', 'for', 'from',
                  'is', 'in', 'into', 'like', 'of', 'off', 'on', 'onto', 'per',
                  'since', 'than', 'the', 'this', 'that', 'to', 'up', 'via',
                  'with']

    r = re.compile(r'\b(%s)\b' % '|'.join(removelist), re.I)
    s = r.sub('', s)

    # if downcode doesn't hit, the char will be stripped here
    s = re.sub('[^-\w\s]', '', s)  # remove unneeded chars
    s = s.strip()                  # trim leading/trailing spaces
    s = re.sub('[-\s]+', '-', s)   # convert spaces to hyphens
    s = s.lower()

    # Trim the line if a character limit has been set.

    d=song()
    d.album.value = "test"
    d.artist.value = "test1"
    print(d.album)
    d.save()
    return s if not num_chars else s[:num_chars]






SERVER_NAME = "127.0.0.1"
SERVER_PORT = 5001
app.config['MONGODB_SETTINGS']={'db':'songs','alias':'default'}
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

if __name__ == '__main__':
    app.run(SERVER_NAME, SERVER_PORT, debug=False, threaded=True)


