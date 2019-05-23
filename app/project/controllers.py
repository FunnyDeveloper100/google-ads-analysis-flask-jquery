from flask import Blueprint, request, \
    g, session, redirect
from app.auth import auth
from app.project.models import Project as ProjectModel

from app.utils.db_models import db


project_app = Blueprint('project_module', __name__, url_prefix='/project')


@project_app.route('/add')
def add_project():
    project_name = request.args.get('project_name')
    country = request.args.get('country')
    user_info = auth.get_user_info()
    project = ProjectModel(user_id=user_info['id'], project_name=project_name, country=country)  # noqa
    db.session.add(project)
    db.session.commit()
    return redirect('/')
