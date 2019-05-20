import functools
import json
import os

import flask

from config import Config
from models import UserModel, ProjectModel
from models.db_model import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

# google auth
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import google_auth
from sqlquery import sql_edit_insert, sql_query2, sql_query
def create_application():
    app = flask.Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    admin = Admin(app)
    admin.add_view(ModelView(UserModel, db.session))
    admin.add_view(ModelView(ProjectModel, db.session))

    return app

app = create_application()
app.register_blueprint(google_auth.app)

@app.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        users = sql_query2("select * from user where email = :email", {"email": user_info['email']})
        if len(users) < 1:
            print 'No exits current user'
            sql_edit_insert("INSERT INTO user (name, family_name, picture, locale, email, given_name, id, verified_email) VALUES (?,?,?,?,?,?,?,?)",(user_info['name'], user_info['family_name'], user_info['picture'], user_info['locale'], user_info['email'], user_info['given_name'], user_info['id'],user_info['verified_email']) )
        else:
            print 'Exist already'

        user_id = user_info['id']
        projects = ProjectModel.query.filter_by(user_id=user_id).all()
        print projects

        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return flask.render_template('home.html', user=user_info, projects=projects)

    return flask.render_template('login.html')

@app.route('/add_project')
def add_project():
    #try :
    print flask.request.args
    project_name = flask.request.args.get('project_name')
    country = flask.request.args.get('country')
    user_info = google_auth.get_user_info()
    print user_info
    project = ProjectModel( user_id=user_info['id'], project_name = project_name, country=country)
    db.session.add(project)
    db.session.commit()
#    sql_edit_insert("INSERT INTO project (user_id, project_name, country) VALUES (?,?,?)", (user_info['id'], project_name, country))
    # except:
    #     print "add error"
    # finally:
    return flask.redirect('/')
