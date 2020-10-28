from dl_core.config import get_alchemy_uri, SQLALCHEMY_BINDS
from flask_sqlalchemy import SQLAlchemy
from dl_core.models.dbrouting import RouteSQLAlchemy


def get_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = get_alchemy_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
    db = RouteSQLAlchemy(app)
    return db
