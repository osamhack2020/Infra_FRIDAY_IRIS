from dl_core import app, db
from dl_core.views import register_api
from flask import render_template
from werkzeug.exceptions import HTTPException
import json
from flask_apscheduler import APScheduler
from datetime import datetime

register_api(app)

from dl_core.models.kma import save_weather_data
from dl_core.views.kma import basic_parse, down_data
sched = APScheduler()
sched.init_app(app)
sched.start()
# 근데 왜 측정값 계속 바뀜?
@sched.task('cron', minute='45', id='down_weather')
def push_weather():
    with app.app_context():
        app.logger.info('start')
        this_time = datetime.now().strftime("%Y%m%d %H")
        src = basic_parse(this_time,down_data(this_time))
        save_weather_data(src)
        app.logger.info('end')

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
# debug mode에서 reloader이 작동해서 2번 삽입되는 문제가 있어서 use_reloader가 False
app.run(host='0.0.0.0', debug=True, use_reloader=False)