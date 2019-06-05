# /app/googleads/models.py
from app.db import db


class GoogleAdwords(db.Model):
    __tablename__ = 'google_adwords'
    id = db.Column(db.Integer, primary_key=True)
    search_terms = db.Column(db.String, nullable=False)
    conversions = db.Column(db.Float, default=0)
    conversion_value = db.Column(db.Float, default=0)
    conversion_rate = db.Column(db.Float)
    avg_cpc = db.Column(db.Float, default=0)
    # impressions = db.Column(db.Integer, default=0)
    # clicks = db.Column(db.Integer, default=0)
    # ctr = db.Column(db.Float, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, search_terms, conversions, conversion_value,
                 conversion_rate, avg_cpc, project_id):

        self.search_terms = search_terms
        self.conversions = conversions
        self.conversion_value = conversion_value
        self.conversion_rate = conversion_rate
        self.avg_cpc = avg_cpc
        # self.impressions = impressions
        # self.clicks = clicks
        # self.ctr = ctr
        self.project_id = project_id

    def __repr__(self):
        return self.search_terms
