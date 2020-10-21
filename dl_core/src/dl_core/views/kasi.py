import json
import xmltodict
from dl_core.secret import key
from datetime import datetime
import requests as req
from calendar import monthrange, monthcalendar

# beautify parsed by xmltodict
def beautify(dirty_dict):
    return json.loads(json.dumps(dirty_dict))

# return tuple (days_of_month, parsed_data)
backup = {}
def get_holiday_tbl(y, m):
    if "%s_%s" % (y, m) in backup:
        return backup["%s_%s" % (y, m)]
    _, ml = monthrange(y, m)
    cur_date = datetime.now()
    URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"
    params = {
        'serviceKey': key,
        'solYear': y,
        'solMonth': "%02d" % m
    }
    res = req.get(URL, params=params)
    dummy = beautify(xmltodict.parse(res.text))[
        'response']['body']
    if not int(dummy['totalCount']):
        return ml, [0 for _ in range(ml)]
    dummy = dummy['items']['item']
    weekends = [(i[5], i[6]) for i in monthcalendar(y, m)]
    weekends = [item for d in weekends for item in d if item != 0]
    hlist = weekends
    if isinstance(dummy, list):
        for dat in dummy:
            d_id = int(dat['locdate'][6:8])
            if dat['isHoliday'] == 'Y' or d_id in weekends:
                hlist.append(d_id) if d_id not in hlist else hlist
    else:
        d_id = int(dummy['locdate'][6:8])
        if dummy['isHoliday'] == 'Y' or d_id in weekends:
                hlist.append(d_id) if d_id not in hlist else hlist
    tbl = [1 if i in hlist else 0 for i in range(1, ml+1)]
    backup["%s_%s" % (y, m)] = (ml,tbl)
    return ml, tbl

# date:datetime obj
def check_holiday(date):
    y = date.year
    m = date.month
    d = date.day
    _, hlist = get_holiday_tbl(y, m)
    return hlist[d-1]

def check_holiday_full(date):
    y = date.year
    m = date.month
    d = date.day
    full_tbl = []
    idx = [m-1, m, m+1]
    mlens = []
    for i in idx:
        param = (y, i)
        if i <= 0:
            param = (y-1, 12)
        elif i > 12:
            param = (y+1, 1)
        ml, hlist = get_holiday_tbl(*param)
        full_tbl.extend(hlist)
        mlens.append(ml)
    offset = [0, mlens[0], mlens[0]+mlens[1]]

    v = offset[idx.index(m)]
    check = {'is_h': full_tbl[v+d-1]}
    check['before_h'] = full_tbl[v+d]
    check['after_h'] = full_tbl[v+d-2]
    for i in range(1, 4):
        if not full_tbl[v+d+i-1]:
            check['before_lh'] = 0
        if not full_tbl[v+d-i-1]:
            check['after_lh'] = 0
    if not 'before_lh' in check:
        check['before_lh'] = 1
    if not 'after_lh' in check:
        check['after_lh'] = 1
    if m == 12 and d >= 21 and d <= 31:
        check['in_end'] = 1
    else:
        check['in_end'] = 0
    return check
