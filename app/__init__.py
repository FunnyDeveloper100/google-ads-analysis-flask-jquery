from flask import Flask, render_template
from config import settings
from app.auth.controllers import google_auth
from app.project.controllers import project_app
from app.auth import auth
from app.utils.db_models import db
from flask_migrate import Migrate
from app.project.models import Project as ProjectModel

# BasicAuth
from flask_basicauth import BasicAuth
# Exception
from werkzeug.exceptions import HTTPException

application = Flask(__name__)
application.config.from_object(settings)
application.register_blueprint(google_auth)
application.register_blueprint(project_app)

db.init_app(application)
migrate = Migrate(application, db)

basic_auth = BasicAuth(application)

from app.admin import addAdminPanel  # noqa
addAdminPanel(application)


@application.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@application.route('/')
def index():
    if auth.is_logged_in():
        user_info = auth.get_user_info()
        user_id = user_info['id']
        projects = ProjectModel.query.filter_by(user_id=user_id).all()
        return render_template('project/project.html', user=user_info, projects=projects)  # noqa

    return render_template('auth/login.html')
