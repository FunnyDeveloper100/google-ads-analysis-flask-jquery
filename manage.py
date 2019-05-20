import os

from app import create_application as app
from flask_script import Manager
from flask_migrate import MigrateCommand

from models.db_model import db

manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
