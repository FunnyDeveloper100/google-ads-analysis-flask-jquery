# /app/project/controller.py

from flask import Blueprint, request, g, session, redirect, render_template, jsonify
from app.auth import google_auth
from app.project.models import Project
from app.db import db
from app.googlesc import g_search_console, GoogleSearchConsole
from app.googleads import g_adwords, GoogleAdwords
from app.utils import func

project_app = Blueprint('project_module', __name__, url_prefix='/project')

# register project_app blueprint to app
def init_app(app):
    app.register_blueprint(project_app)

# add new project with name, property url, country
@project_app.route('/add/')
def add():
    project_name = request.args.get('project_name')
    property_url = request.args.get('property_url')
    country = request.args.get('country')
    user_info = google_auth.get_user_info()
    project = Project(user_id=user_info['id'], project_name=project_name, property_url=property_url, country=country)  # noqa
    if (project is not None):
        db.session.add(project)
        db.session.commit()

    return redirect('/')

# update project info
@project_app.route('/edit/<id>/')
def edit(id):
    if id is not None:
        project = getProjectById(id)
        project_name = request.args.get('project_name')
        property_url = request.args.get('property_url')
        country = request.args.get('country')
        project.project_name = project_name
        project.property_url = property_url
        project.country = country
        db.session.commit()

    return redirect('/')

# delete project by id
@project_app.route('/delete/<id>/')
def delete(id):
    GoogleSearchConsole.query.filter_by(project_id=id).delete()
    Project.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/')

# view project data by id
@project_app.route('/view/<id>/')
def view(id):
    project = getProjectById(id)
    gsc_data = g_search_console.getData(id)
    gads_data = g_adwords.getData(id)
    table = join_ads_sc(id)
    return render_template('project/project_detail.html', project=project, joined_data = table)

# newly load data
@project_app.route('/load/<id>/')
def load(id):
    project = getProjectById(id)
    range = request.args.get('daterange')
    start_date, end_date = func.getStartEndDate(range)
    g_search_console.store_data(project, start_date, end_date)
    g_adwords.store_adwords(id, start_date, end_date)
    return redirect('/project/view/{}/'.format(id))


# get project instance by id
def getProjectById(id):
    return Project.query.filter_by(id=id).first()

def join_ads_sc(id):
    _table = GoogleAdwords.query.outerjoin(GoogleSearchConsole, (GoogleSearchConsole.project_id==id) & (GoogleSearchConsole.keys == GoogleAdwords.search_terms)).add_columns(
        GoogleAdwords.search_terms,
        GoogleAdwords.conversions,
        GoogleAdwords.conversion_value,
        GoogleAdwords.conversion_rate,
        GoogleAdwords.avg_cpc,
        GoogleSearchConsole.position
        ).filter(GoogleAdwords.project_id==id).all()
    return _table