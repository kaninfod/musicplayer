#!flask/bin/python
from app import app


SERVER_NAME = "127.0.0.1"
SERVER_PORT = 5000
app.debug = False
app.run(SERVER_NAME, SERVER_PORT, threaded=True)
