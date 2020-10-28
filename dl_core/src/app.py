from dl_core import app, db
from dl_core.views import register_api
from flask import render_template
from werkzeug.exceptions import HTTPException
import json

register_api(app)

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

app.run(host='0.0.0.0', debug=True)