__author__ = 'martin'
from flask import Flask, session, g
from flask.ext.mongoengine import MongoEngine
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {'DB': "songs"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"
db = MongoEngine(app)

cache = SimpleCache()

from app import views, models



