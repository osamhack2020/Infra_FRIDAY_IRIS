from dl_core import app#, db
from dl_core.views import register_api
from flask import render_template

register_api(app)
# @app.route('/', methods=['GET'])
# def read_qrcode():
#     return render_template("index.html")

app.run(host='0.0.0.0', debug=True)