from flask import Flask
from flask_migrate import Migrate
from dl_core.models import get_db

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
db = get_db(app)
migrate = Migrate(app, db)
from dl_core.models.models import init_db
init_db()