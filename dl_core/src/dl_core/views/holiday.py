import json
import xmltodict
import requests as req
from flask import Blueprint
from datetime import datetime
from dl_core.secret import key
from calendar import monthrange

holiday = Blueprint('holiday', __name__, url_prefix='/holiday')

def beautify(dirty_dict):
    return json.loads(json.dumps(dirty_dict))

def get_month_holiday(year, month):
    URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"
    params = {
        'serviceKey':key,
        'solYear':year,
        'solMonth':month
    }
    res = req.get(URL, params=params)
    dummy = beautify(xmltodict.parse(res.text))['response']['body']['items']['item']
    if isinstance(dummy, list):
        return [(sheet['locdate'], sheet['isHoliday']) for sheet in dummy]
    else:
        return [(dummy['locdate'], dummy['isHoliday'])]

@holiday.route('/check/<date>', methods=['GET'])
def check_holiday(date):
    y = date[0:4]
    m = date[4:6]
    d = date[6:8]
    week_idx = datetime(int(y), int(m), int(d)).weekday()
    if week_idx == 5 or week_idx == 6:
        return json.dumps({"is_holiday":True}) 
    m_h_list = get_month_holiday(y, m)
    for h in m_h_list:
        if date == h[0] and h[1] == 'Y':
            res = {"is_holiday": True}
            return json.dumps(res)
    return json.dumps({"is_holiday": False})

@holiday.route('/check/month/<int:month>', methods=['GET'])
def check_month_holiday(month):
    check_data = {"month":month}
    year = datetime.today().year
    m_h_list = get_month_holiday(year, "%02d" % month)
    day_n = monthrange(year, month)[1]
    day_check = {}
    test = []
    for day in range(1,day_n+1):
        date_str = str(year) + "%02d" % month + "%02d" % day
        week_idx = datetime(year, month, day).weekday()
        if date_str not in m_h_list:
            if week_idx != 5 and week_idx != 6:
                day_check[date_str] = False
                continue
        day_check[date_str] = True
    check_data['body'] = day_check
    return json.dumps(check_data), 200
