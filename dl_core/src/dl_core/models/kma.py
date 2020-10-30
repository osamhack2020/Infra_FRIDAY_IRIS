from dl_core import db
from dl_core.models.models import run_query, already_exist, DailyWeather
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

def save_weather_data(parse_data):
    if not already_exist_weather(parse_data["date"], parse_data["h"]):
        run_query(insert_weather_data, ([parse_data]))
