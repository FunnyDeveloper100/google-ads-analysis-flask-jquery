from flask import render_template
from app import application
from app.auth import auth
from config import settings

if __name__ == '__main__':
    application.run(
        host='0.0.0.0',
        port=settings.PORT,
        debug=settings.DEBUG
    )
