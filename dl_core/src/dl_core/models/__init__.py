from attendance_check.config import get_alchemy_uri
from flask_sqlalchemy import SQLAlchemy

def get_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = get_alchemy_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db = SQLAlchemy(app)
    return db