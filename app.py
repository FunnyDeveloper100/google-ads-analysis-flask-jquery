import functools
import json
import os

import flask

from config import Config
from models import UserModel
from models.db_model import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

# google auth
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import google_auth

def create_application():
    app = flask.Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    admin = Admin(app)
    admin.add_view(ModelView(UserModel, db.session))

    return app

app = create_application()
app.register_blueprint(google_auth.app)

@app.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return flask.render_template('home.html', user=user_info)

    return flask.render_template('login.html')
