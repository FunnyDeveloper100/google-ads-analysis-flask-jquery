# /app/project/controller.py

from flask import Blueprint, request, g, session, redirect, render_template, jsonify
import datetime
from app.auth import google_auth
from app.project.models import Project
from app.db import db
from app.googlesc import g_search_console, GoogleSearchConsole
from app.googleads import g_adwords, GoogleAdwords
from app.utils import func
from threading import Thread
from flask import current_app
import pandas as pd
import functools

project_app = Blueprint('project_module', __name__, url_prefix='/project')

# register project_app blueprint to app
def init_app(app):
    app.register_blueprint(project_app)

@project_app.route('/')
def projects():
    user_info = google_auth.get_user_info()
    user_id = user_info['id']
    projects = Project.query.filter_by(user_id=user_id).all()
    service = google_auth.get_webmasters_service()
    property_urls = g_search_console.get_property_urls(service)
    return render_template('project/project_list.html', user=user_info, projects=projects, property_urls=property_urls)

# add new project with name, property url, country
@project_app.route('/add/')
def add():
    project_name = request.args.get('project_name')
    property_url = request.args.get('property_url')
    country = request.args.get('country')

    if (project_name is None) or (property_url is None) or (country is None):
        return jsonify({'status': 'error'})

    user_info = google_auth.get_user_info()
    project = Project(user_id=user_info['id'], project_name=project_name, property_url=property_url, country=country)  # noqa
    if (project is not None):
        db.session.add(project)
        db.session.commit()

    storing_thread(project.id, get_last_12month())
    
    # return jsonify({
    #     'project': {
    #         'id': project.id,
    #         'name': project.project_name,
    #         'url': project.property_url,
    #         'country': project.country
    #     }
    # })
    return redirect('/project/')

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

    return redirect('/project/')

# delete project by id
@project_app.route('/delete/<id>/')
def delete(id):
    g_search_console.deleteAll(id)
    g_adwords.deleteAll(id)
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

# load data from google server
def store_database(application, service, client, id, date_range):
    with application.test_request_context():
        start_date, end_date = func.getStartEndDate(date_range)
        project = getProjectById(id)
        g_search_console.store_data(service, project, start_date, end_date)
        g_adwords.store_adwords(client, id, start_date, end_date)

def storing_thread(id, date_range, isAsync = True):
    application = current_app._get_current_object()
    service = google_auth.get_webmasters_service()
    client = google_auth.get_adwords_client()
    if isAsync is True:
        thr = Thread(target=store_database, args=[application, service, client, id, date_range])
        thr.start()
    else:
        store_database(application, service, client, id, date_range)

# newly load data
@project_app.route('/load/<id>/')
def load(id):
    date_range = request.args.get('daterange')
    storing_thread(id, date_range)
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

    weighted(_table)

    return _table

def get_last_12month():
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)
    return '{0}-{1}'.format(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))

def getMaxPos_Rate(_table):
    if len(_table) < 1:
        return 0, 0

    max_pos = 0.0
    sum_rate = 0.0

    for row in _table:
        if row.position is not None and max_pos < row.position:
            max_pos = row.position
        if row.conversion_rate is not None:
            sum_rate += row.conversion_rate
    return max_pos, sum_rate / len(_table)

def weighted(_table):
    mv, ab = getMaxPos_Rate(_table)
    lth = len(_table)
    for i in range(lth - 1):
        for j in range(i + 1, lth):
            a = _table[i]
            b = _table[j]
            a_etv = get_etv(a.position, a.conversion_rate, mv, ab)
            b_etv = get_etv(b.position, b.conversion_rate, mv, ab)
            if a_etv < b_etv:
                _table[i], _table[j] = _table[j], _table[i]

    return _table

def get_etv(v, b, mv, ab):
    if mv == 0:
        return 0
    
    v = 0 if v is None else v
    b = 0 if b is None else b
    return v / mv * b + (1 - v / mv) * ab