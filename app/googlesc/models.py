# /app/googlesc/models.py

from app.db import db

class GoogleSearchConsole(db.Model):
    __tablename__ = 'google_search_console'
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