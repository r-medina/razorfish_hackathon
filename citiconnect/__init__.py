import os
from flask import Flask

from mongoengine import connect
from flask.ext.mongoengine import MongoEngine

DEBUG = True
SECRET_KEY = 'd\xd5\xae\xd1\x03zF&\xd7\x7f\xe4\x89=\xbc99\x96UK\x8b\xbcK\xe2\x9b'

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY)

DB_NAME = 'citiconnect'
#DB_USERNAME = 'citiconnectdb'
#DB_PASSWORD = 'prep4prep'
#DB_HOST_ADDRESS = 'dbh74.mongolab.com:27747/citiconnect'

# Declations for connecting to the mongodb database
app.config["MONGODB_DB"] = DB_NAME
#connect(DB_NAME, host='mongodb://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOST_ADDRESS)
connect(DB_NAME)
db = MongoEngine(app)

import citiconnect.views
import connect_score

if __name__ == '__main__':
    app.run()
