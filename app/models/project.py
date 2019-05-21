from .db_model import db

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(128))
    country = db.Column(db.String(128))
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)
