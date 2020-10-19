from datetime import datetime, timedelta
from flask import Blueprint
import json
from dl_core.views.kma import get_normal_data, get_month_data
weather = Blueprint('weather', __name__, url_prefix='/weather')

@weather.route('/<date>', methods=['GET'])
def get_target_weather_data(date):
    res = json.dumps(get_normal_data(date))
    return res, 200

@weather.route('/year/<int:year>', methods=['GET'])
def get_year_weather_data(year):
    res = {"year":year}
    month = {}
    for m in range(1,13):
        month[m] = get_month_data(year, m)
    res['body'] = month
    return res, 200

@weather.route('/month/<int:month>', methods=['GET'])
def get_month_weather_data(month):
    year = datetime.today().year
    return get_month_data(year, month), 200

@weather.route('/yesterday', methods=['GET'])
def get_yesterday_weather_data():
    yesterday = (datetime.today()-timedelta(1)).strftime("%Y%m%d")
    return get_target_weather_data(yesterday)
