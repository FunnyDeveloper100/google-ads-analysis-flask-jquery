from db_model import db

class User(db.Model):
    family_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    picture = db.Column(db.String, nullable=False)
    locale = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    given_name = db.Column(db.String(128), index=True, nullable=False)
    id = db.Column(db.String(128), primary_key=True, nullable=False)
    verified_email = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def __init__(self, name, family_name, picture, locale, email, given_name, id, verified_email):
        self.family_name = family_name
        self.name = name
        self.picture = picture
        self.locale = locale
        self.email = email
        self.given_name = given_name
        self.id = id
        self.verified_email = verified_email
