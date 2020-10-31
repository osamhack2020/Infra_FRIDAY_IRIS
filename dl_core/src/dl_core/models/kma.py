from dl_core import db
from dl_core.models.models import run_query, already_exist, DailyWeather, DateMealtimeMapping
mealtime_map = {
    "breakfast": "7:10",
    "lunch": "11:13",
    "dinner": "17:20"
}
# 인자를 걍 튜플로 받아도 될듯
def _already_exist_weather(date, h):
    row = db.session.using_bind("slave").query(DailyWeather).filter_by(date=date, h=h).first()
    if row:
        return True
    else:
        return False
        
def already_exist_weather(date, h):
    return run_query(_already_exist_weather, (date, h))

def insert_weather_data(parse_data):
    if not already_exist_weather(parse_data["date"], parse_data["h"]):
        new_w = DailyWeather(
            date = parse_data["date"],
            h = parse_data["h"],
            t = parse_data["t"],
            hm = parse_data["hm"],
            ws = parse_data["ws"],
            rain = parse_data["rain"],
            snow = parse_data["snow"]
        )
        sess = db.session.using_bind("master")
        sess.add(new_w)
        sess.commit()
        sess.flush()

def _get_weather_data(date, h):
    parse_data = {}
    row = db.session.using_bind("slave").query(DailyWeather).filter_by(date=date, h=h).first()
    if row:
        parse_data["t"] = row.t
        parse_data["hm"] = row.hm
        parse_data["ws"] = row.ws
        parse_data["rain"] = row.rain
        parse_data["snow"] = row.snow
    return parse_data

def get_weather_data(date_id):
    weather_data = {}
    d, m = parse_date_id(date_id)
    st, end = map(int, mealtime_map[m].split(":"))
    sum_t = sum_ws = 0.0
    sum_hm = 0
    rain = snow = 0
    for h in range(st, end+1):
        parse_data = run_query(_get_weather_data, (d, h))
        sum_t += parse_data["t"]
        sum_hm += parse_data["hm"]
        sum_ws += parse_data["ws"]
        rain = parse_data["rain"] if parse_data["rain"] else rain
        snow = parse_data["snow"] if parse_data["snow"] else snow
    hlen = end - st + 1
    weather_data["rain"] = rain
    weather_data["snow"] = snow
    weather_data["t"] = sum_t / hlen
    weather_data["hm"] = sum_hm / hlen
    weather_data["ws"] = sum_ws / hlen
    return weather_data

def save_weather_data(parse_data):
    if not already_exist_weather(parse_data["date"], parse_data["h"]):
        run_query(insert_weather_data, ([parse_data]))

def get_date_info(did):
    row = db.session.using_bind("slave").query(DateMealtimeMapping).filter_by(id=did).first()
    if row:
        return row.korean_date, row.meal_time
    else:
        return '', ''

def get_month(did):
    d, m = parse_date_id(did)
    return d.month
    
def parse_date_id(did):
    d, m = run_query(get_date_info, ([did]))
    if d and m:
        return d, m

def exist_weather(date_id):
    date, mealtime = parse_date_id(date_id)
    # 변환..?
    # date = date.replace('-', '')
    st, end = map(int, mealtime_map[mealtime].split(":"))
    for h in range(st, end+1):
        if not already_exist_weather(date, h):
            return False
    return True