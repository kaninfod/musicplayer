__author__ = 'martin'
from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {'DB': "songs"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"
db = MongoEngine(app)
#app.config['MONGODB_SETTINGS']={'db':'songs','alias':'default'}

from app import views, models



