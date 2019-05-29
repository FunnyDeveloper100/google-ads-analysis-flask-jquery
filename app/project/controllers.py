from flask import Blueprint, request, \
    g, session, redirect, render_template
from app.auth import auth
from app.project.models import Project
from app.project.models import GscSearchTerm
from app.project.models import GadsSearchTerm

from app.utils.db_models import db
from app.utils.search_console import get_search_terms
from app.utils.googleads import getAdsData
from datetime import date, timedelta
from app.utils.func import string_to_float, string_to_int, percent_to_float, dollar_to_float

project_app = Blueprint('project_module', __name__, url_prefix='/project')

@project_app.route('/add/')
def add_project():
    project_name = request.args.get('project_name')
    property_url = request.args.get('property_url')
    country = request.args.get('country')
    user_info = auth.get_user_info()
    project = Project(user_id=user_info['id'], project_name=project_name, property_url=property_url, country=country)  # noqa
    db.session.add(project)
    db.session.commit()

    # first pull data and store to database
    if (project):
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        store_search_terms(project, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        pull_gads_data(project, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    return redirect('/')

@project_app.route('/edit/<id>')
def edit_project(id):
    if id is not None:
        project = Project.query.filter_by(id=id).first()
        project_name = request.args.get('project_name')
        property_url = request.args.get('property_url')
        country = request.args.get('country')
        project.project_name = project_name
        db.session.commit()

    return redirect('/')

@project_app.route('/view/<id>/')
def view_project(id):
    project = Project.query.filter_by(id=id).first()

    range = request.args.get('daterange')
    if (range):
        params = range.split("~")
        store_search_terms(project, params[0], params[1])

         #pull google adwords data
        pull_gads_data(project, params[0], params[1])

    gsc_keys = GscSearchTerm.query.filter_by(project_id=id).all()
    gads_search_terms = GadsSearchTerm.query.filter_by(project_id=id).all()
    joined_data = join_tables()
    return render_template('project/project_detail.html', project=project, gsc_keys=gsc_keys, gads_search_terms=gads_search_terms, joined_data = joined_data)

@project_app.route('/delete_project/<id>/')
def delete_project(id):
    GscSearchTerm.query.filter_by(project_id=id).delete()
    GadsSearchTerm.query.filter_by(project_id=id).delete()
    Project.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/')

def store_search_terms(project, start_date, end_date):
    service = auth.get_service()
    GscSearchTerm.query.filter_by(project_id=project.id).delete()
    response = get_search_terms(service, project.property_url,  start_date, end_date)
    if 'rows' in response:
        for row in response['rows']:
            insert_gsc_row(row, project.id)

def insert_gsc_row(row, project_id):
    item = GscSearchTerm(row['keys'][0], row['position'], project_id)
    db.session.add(item)
    db.session.commit()



def pull_gads_data(project, start_date, end_date):
    GadsSearchTerm.query.filter_by(project_id=project.id).delete()
    gads_data = getAdsData('Search Term Test Data.csv')

    for index, row in gads_data.iterrows():
        store_gads_data(project.id, row)

def store_gads_data(_id, _data):
    item = GadsSearchTerm(
        _data['Search term'],
        _data['Conversions'],
        string_to_float(_data['Conv. value']),
        percent_to_float(_data['Conv. rate']),
        _data['Avg. CPC'],
        (_data['Impressions']),
        (_data['Clicks']),
        percent_to_float(_data['CTR']),
        _id)
    db.session.add(item)
    db.session.commit()


def join_tables():
    _table = GadsSearchTerm.query.outerjoin(GscSearchTerm, GscSearchTerm.keys == GadsSearchTerm.search_terms).add_columns(
        GadsSearchTerm.search_terms,
        GadsSearchTerm.conversions,
        GadsSearchTerm.conversion_value,
        GadsSearchTerm.conversion_rate,
        GadsSearchTerm.avg_cpc,
        GscSearchTerm.position
        ).all()
    return _table
