import functools
import json
import os

from flask import Flask, render_template, request, redirect, Response

from .config import Config

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import sqla

from flask_migrate import Migrate

#BasicAuth
from flask_basicauth import BasicAuth

# Google Auth
from . import google_auth

#Exception
from werkzeug.exceptions import HTTPException

from . import models
from .models.db_model import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = 'password'
    db.init_app(app)
    migrate = Migrate(app, db)

    return app

app = create_app()

# set google auth
app.register_blueprint(google_auth.app)

# basic auth
basic_auth = BasicAuth(app)

@app.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        users = models.UserModel.query.filter_by(email=user_info['email']).all()
        if len(users) < 1:
            print('This user is new')
            user = models.UserModel(user_info['name'], user_info['family_name'], user_info['picture'], user_info['locale'], user_info['email'], user_info['given_name'], user_info['id'],user_info['verified_email'], 0)
            db.session.add(user)
            db.session.commit()
        else:
            print('This user exist already')

        user_id = user_info['id']
        projects = models.ProjectModel.query.filter_by(user_id=user_id).all()
        return render_template('home.html', user=user_info, projects=projects)

    return render_template('login.html')

@app.route('/add_project')
def add_project():
    project_name = request.args.get('project_name')
    country = request.args.get('country')
    user_info = google_auth.get_user_info()
    project = models.ProjectModel( user_id=user_info['id'], project_name = project_name, country=country)
    db.session.add(project)
    db.session.commit()
    return redirect('/')

class AuthException(HTTPException):
    def __init__(self, message):
        # # python 2
        # super(AuthException, self).__init__(message, Response(
        #     message, 401,
        #     {'WWW-Authenticate': 'Basic realm="Login Required"'}
        # ))
        # python 3
        super().__init__(message, Response(
            message, 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ModelView(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated. Are you a administrator?')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())

def addAdminPanel(app):
    admin = Admin(app)
    admin.add_view(ModelView(models.UserModel, db.session))
    admin.add_view(ModelView(models.ProjectModel, db.session))

addAdminPanel(app)
