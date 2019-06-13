from app.db import db

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(128))
    country = db.Column(db.String(128))
    property_url = db.Column(db.String)
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'))
    
    google_search_console = db.relationship('GoogleSearchConsole', backref='project')
    google_adwords = db.relationship('GoogleAdwords', backref='project')

    def __init__(self, project_name, country, property_url, user_id):
        self.project_name = project_name
        self.country = country
        self.property_url = property_url
        self.user_id = user_id

    def __repr__(self):
        return self.project_name

