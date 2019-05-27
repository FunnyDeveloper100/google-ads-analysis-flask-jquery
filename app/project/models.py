from app.utils.db_models import db

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(128))
    country = db.Column(db.String(128))
    property_url = db.Column(db.String)
    gsc_search_terms = db.relationship('GscSearchTerm', backref='project')
    gads_search_terms = db.relationship('GadsSearchTerm', backref='project')
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'))


    def __init__(self, project_name, country, property_url, user_id):
        self.project_name = project_name
        self.country = country
        self.property_url = property_url
        self.user_id = user_id

    def __repr__(self):
        return self.project_name

class GadsSearchTerm(db.Model):
    __tablename__ = 'gads_search_term'
    id = db.Column(db.Integer, primary_key=True)
    search_terms = db.Column(db.String, nullable=False)
    conversions = db.Column(db.Float, default=0)
    conversion_value = db.Column(db.Float, default=0)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    ctr = db.Column(db.Float, default=0)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, search_terms, conversions, conversion_value, impressions, clicks, ctr, project_id):
        self.search_terms = search_terms
        self.conversions = conversions
        self.conversion_value = conversion_value
        self.impressions = impressions
        self.clicks = clicks
        self.ctr = ctr
        self.project_id = project_id

    def __repr__(self):
        return self.search_terms


class GscSearchTerm(db.Model):
    __tablename__ = 'gsc_search_term'
    id = db.Column(db.Integer, primary_key=True)
    keys = db.Column(db.String, nullable=False)
    position = db.Column(db.Float, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, keys, position, project_id):
        self.keys = keys
        self.position = position
        self.project_id = project_id

    def __repr__(self):
        return self.keys


