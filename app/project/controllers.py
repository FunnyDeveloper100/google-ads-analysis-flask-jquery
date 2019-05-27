from flask import Blueprint, request, \
    g, session, redirect, render_template
from app.auth import auth
from app.project.models import Project as ProjectModel
from app.project.models import GscSearchTerm as GscSearchTermModel
from app.project.models import GadsSearchTerm as GadsSearchTermModel

from app.utils.db_models import db
from app.utils.search_console import get_search_terms
from app.utils.googleads import getAdsData
from datetime import date, timedelta
from app.utils.func import string_to_float, string_to_int, percent_to_float

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
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        store_search_terms(project, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        pull_gads_data(project, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    return redirect('/')

@project_app.route('/view/<id>/')
def view_project(id):
    project = ProjectModel.query.filter_by(id=id).first()
    range = ""
    range = request.args.get('daterange')
    if (range):
        params = []
        params = range.split("~")
        store_search_terms(project, params[0], params[1])

         #pull google adwords data
        pull_gads_data(project, params[0], params[1])

    gsc_keys = GscSearchTermModel.query.filter_by(project_id=id).all()
    gads_search_terms = GadsSearchTermModel.query.filter_by(project_id=id).all()

    return render_template('project/project_detail.html', project=project, gsc_keys=gsc_keys, gads_search_terms=gads_search_terms)

def store_search_terms(project, start_date, end_date):
    service = auth.get_service()
    GscSearchTermModel.query.filter_by(project_id=project.id).delete()
    response = get_search_terms(service, project.property_url,  start_date, end_date)
    if 'rows' in response:
        for row in response['rows']:
            insert_gsc_row(row, project.id)

def insert_gsc_row(row, project_id):
    item = GscSearchTermModel(row['keys'][0], row['position'], project_id)
    db.session.add(item)
    db.session.commit()

def pull_gads_data(project, start_date, end_date):
    GadsSearchTermModel.query.filter_by(project_id=project.id).delete()
    gads_data = getAdsData('googleads.csv')

    for index, row in gads_data.iterrows():
        store_gads_data(project.id, row)

def store_gads_data(_id, _data):
    item = GadsSearchTermModel(_data['Search term'], _data['All conv.'], string_to_float(_data['All conv. value']), string_to_int(_data['Impr.']), string_to_int(_data['Clicks']), percent_to_float(_data['CTR']), _id)
    db.session.add(item)
    db.session.commit()
