from flask import Response
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import sqla

from werkzeug.exceptions import HTTPException
from app.auth.models import User as UserModel
from app.project.models import Project as ProjectModel
from app.utils.db_models import db

# BasicAuth
from app import basic_auth


def addAdminPanel(app):
    admin = Admin(app)
    admin.add_view(ModelView(UserModel, db.session))
    admin.add_view(ModelView(ProjectModel, db.session))


class ModelView(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated. Are you a administrator?')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            message, 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))
