import json
from flask import Blueprint
from datetime import datetime
from calendar import monthrange

from dl_core.secret import key
from dl_core.views.kasi import check_holiday, check_holiday_full

holiday = Blueprint('holiday', __name__, url_prefix='/holiday')


@holiday.route('/check/<date>', methods=['GET'])
def check_day(date):
    y, m, d = int(date[:4]), int(date[4:6]), int(date[6:8])
    check = {"isHoliday": check_holiday(datetime(y, m, d))}
    return json.dumps(check), 200


@holiday.route('/check/month/<int:m>', methods=['GET'])
def check_month(m):
    y = datetime.now().year
    _, ml = monthrange(y, m)
    check = {}
    for i in range(1, ml+1):
        check[str(i)] = {"isHoliday":check_holiday(datetime(y, m, i))}
    return json.dumps(check), 200


@holiday.route('/check/full/<date>', methods=['GET'])
def check_day_full(date):
    y, m, d = int(date[:4]), int(date[4:6]), int(date[6:8])
    return json.dumps(check_holiday_full(datetime(y, m, d))), 200


@holiday.route('/check/full/month/<int:m>', methods=['GET'])
def check_month_full(m):
    y = datetime.now().year
    _, ml = monthrange(y, m)
    check = {}
    for i in range(1, ml+1):
        check[str(i)] = check_holiday_full(datetime(y, m, i))
    return json.dumps(check), 200
