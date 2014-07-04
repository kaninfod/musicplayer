from app import app, models
from flask import render_template
from flask import request
from flask import url_for
import os
import time


@app.route('/')
@app.route('/artists')
@app.route('/artists/page/<page>')
def artists(page=1):

    qstr = (request.args.get("q",""))
    if qstr:
        data = models.artist.objects(albumartist__icontains=qstr)
    else:
        data = models.artist.objects().order_by('albumartist')

    p = models.paginate(page,10)
    p.total_documents = data.count()
    data = data[p.min:p.max]

    return render_template('artists.html', data=data, paginate=p, q=qstr)

@app.route('/albums')
@app.route('/albums/artist/<artist_id>/page/<page>')
@app.route('/albums/artist/<artist_id>')
@app.route('/albums/page/<page>')
def albums(page=1, artist_id=None):



    qstr = (request.args.get("q",""))


    if qstr:
        data = models.album.objects(albumtitle__icontains=qstr)
        breadcrumb = [['All Artists','/artists'],
                      ['Albums', '/albums'],
                      ["Serach for '%s'" % qstr,'/albums/artist/%s' % artist_id]]
    elif artist_id:
        data = models.album.objects(albumartist=artist_id)
        breadcrumb = [['All Artists','/artists'],
                [data[0].albumartist.albumartist,'/albums/artist/%s' % artist_id]]
    else:
        data = models.album.objects()
        breadcrumb = [['All Artists','/artists'],
                ['Albums','#']]

    p = models.paginate(page,10)
    p.total_documents = data.count()
    data = data[p.min:p.max]

    return render_template('albums.html', data=data, paginate=p, q=qstr, breadcrumb=breadcrumb)

@app.route('/songs')
@app.route('/songs/album/<album_id>/page/<page>')
@app.route('/songs/album/<album_id>')
@app.route('/songs/page/<page>')
def songs(page=1, album_id=""):

    qstr = (request.args.get("q",""))

    if qstr:
        data = models.song.objects(songtitle__icontains=qstr)
        breadcrumb = [['All Artists','/artists'],
              ['Albums', '/albums'],
              ['Songs', '/songs'],
              ["Serach for '%s'" % qstr,'']]
    elif album_id:

        data = models.song.objects(album=album_id).order_by('tracknumber')
        breadcrumb = [  ['All Artists','/artists'],
                        [data[0].artist,'/albums/artist/%s' % data[0].albumartist.id],
                        [data[0].album.albumtitle,'#']
                    ]
    else:
        data = models.song.objects()
        breadcrumb = [  ['Artists','/artists'],
                        ['Albums','/albums'],
                        ['Songs','#']]

    p = models.paginate(page,10)
    p.total_documents = data.count()
    data = data[p.min:p.max]


    try:
        #mb = models.musicbrainz(data[0].album)
        album = data[0].album
        cover_url = album.get_coverart_url()
        cover_url = "/static/media/%s" % (cover_url)
    except Exception as e:
        cover_url = "/static/img/generic_album_cover.jpg"

    return render_template('songs.html', data=data, paginate=p, q=qstr, url=cover_url, breadcrumb=breadcrumb)

def url_for_other_page(**kwargs):
    args = request.view_args.copy()
    for key, value in kwargs.items():
            args[key] = value
    return url_for(request.endpoint, **args)

@app.route('/playsong', methods=['GET', 'POST'])
def playsong():
    song_id = (request.args.get("song_id",""))

    song_object = models.song.objects(id=song_id).first()
    #song_object = response.data[0]
    mediapath = "/home/martin/python/musicplayer/app/static/media/"
    songlink = "%s.mp3" % (song_object.id)
    songpath = mediapath + songlink

    filepath = song_object.filepath
    try:
        os.symlink(filepath, songpath)
    except FileExistsError:
        os.remove(songpath)
        os.symlink(filepath, songpath)


    return render_template('songplay.html', title = song_object.songtitle, song=songlink)


@app.route('/updatedb')
def updatedb():

    models.add_collection("/media/store/Music")
    return 0

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404



@app.route('/sg/<album_id>')
def sg(album_id):
    sng = models.album.objects(id=album_id).first()
    mb = models.musicbrainz(sng)
    mb.get_coverart()
    url = mb.get_coverart_url()

    return render_template('showimg.html', img = "static/media/%s" % (url))




@app.route('/dbstatus')
def dbstatus():
    try:
        cache
    except KeyError:
        return "-1"
        #return render_template("dbstatus.html", status= -1)
    else:
        return str(cache)
        #return render_template("dbstatus.html", status=cache['songcounter'])


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


app.jinja_env.globals['url_for_other_page'] = url_for_other_page

