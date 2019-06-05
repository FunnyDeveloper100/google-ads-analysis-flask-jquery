from app.db import db
from app.utils import admin
from flask import Flask, render_template
from flask_migrate import Migrate
from config import settings
from app.auth import google_auth, basic_auth
from app.project import project, Project

# import models
from app.auth.models import User

application = Flask(__name__)
application.config.from_object(settings)

# init admin
admin.addAdminPanel(application)

# set database
db.init_app(application)
migrate = Migrate(application, db)

# register auth modules
google_auth.init_app(application)
basic_auth.init_app(application)

# register blueprint
project.init_app(application)

# router
# 404 error
@application.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# index
@application.route('/')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        user_id = user_info['id']
        projects = Project.query.filter_by(user_id=user_id).all()
        return render_template('project/project_list.html', user=user_info, projects=projects)
    else:
        return render_template('auth/login.html')
