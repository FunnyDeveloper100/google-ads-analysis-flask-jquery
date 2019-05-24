from flask import Blueprint, request, \
    g, session, redirect, render_template
from app.auth import auth
from app.project.models import Project as ProjectModel
from app.project.models import GscSearchTerm as GscSearchTermModel

from app.utils.db_models import db
from app.utils.search_console import get_search_terms

project_app = Blueprint('project_module', __name__, url_prefix='/project')

@project_app.route('/add')
def add_project():
    project_name = request.args.get('project_name')
    property_url = request.args.get('property_url')
    country = request.args.get('country')
    user_info = auth.get_user_info()
    project = ProjectModel(user_id=user_info['id'], project_name=project_name, property_url=property_url, country=country)  # noqa
    db.session.add(project)
    db.session.commit()

    # first pull data and store to database
    if (project):
        store_search_terms(project)

    return redirect('/')

@project_app.route('/view/<id>')
def view_project(id):
    project = ProjectModel.query.filter_by(id=id).first()
    terms = GscSearchTermModel.query.filter_by(project_id=id).all()
    return render_template('project/project_detail.html', project=project, terms=terms)

def store_search_terms(project):
    service = auth.get_service()
    response = get_search_terms(service, project.property_url, "2019-05-01", "2019-05-05")
    if 'rows' in response:
        for row in response['rows']:
            insert_row(row, project.id)

def insert_row(row, project_id):
    item = GscSearchTermModel(row['keys'][0], row['position'], project_id)
    dup = GscSearchTermModel.query.filter_by(keys=item.keys).first()
    if (dup):
        dup.position = item.position
    else:
        db.session.add(item)
    db.session.commit()

