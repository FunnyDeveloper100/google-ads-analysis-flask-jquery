from app.utils.db_models import db


class User(db.Model):
    __tablename__ = 'user'
    family_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    picture = db.Column(db.String, nullable=False)
    locale = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    given_name = db.Column(db.String(128), index=True, nullable=False)
    id = db.Column(db.String(128), primary_key=True, nullable=False)
    verified_email = db.Column(db.Boolean)
    role = db.Column(db.Integer, default=0)
    projects = db.relationship('Project', backref='user')

    def __repr__(self):
        return self.name

    def __init__(self, user):
        self.family_name = user['family_name']
        self.name = user['name']
        self.picture = user['picture']
        self.locale = user['locale']
        self.email = user['email']
        self.given_name = user['given_name']
        self.id = user['id']
        self.verified_email = user['verified_email']
        self.role = user['role']
