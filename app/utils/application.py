from flask import Flask
from config import settings
from app.auth.controllers import google_auth
from app.project.controllers import project_app


def create_application():
    application = Flask(__name__)
    application.config.from_object(settings)
    application.register_blueprint(google_auth)
    application.register_blueprint(project_app)

    return application
