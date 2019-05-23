from app.utils.db_models import db


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(128))
    country = db.Column(db.String(128))
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'))

    def __init__(self, project_name, country, user_id):
        self.project_name = project_name
        self.country = country
        self.user_id = user_id

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)
