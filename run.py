#!flask/bin/python
from app import app


SERVER_NAME = "127.0.0.1"
SERVER_PORT = 5000
app.run(SERVER_NAME, SERVER_PORT, debug=False, threaded=True)
#app.run(debug = False)