from calendar import monthrange
from datetime import datetime
import json
import requests as req
from dl_core.secret import key
from dl_core.models.kma import get_weather_data, get_month, parse_date_id
from dl_core import app
rs = ["None", "Rain", "Both", "Snow", "Rain", "Rain", "Both","Snow"]
#
# ta : 온도, ws : 풍속, hm : 습도
# cloud : 구름 양, rain : 강수량, snow : 적설량 
#
def get_cloud_level(c_v):
    if c_v <= 2.0:
        return "clear"
    elif c_v <=5.0:
        return "little cloudy"
    elif c_v <= 8.0:
        return "cloudy"
    else:
        return "grey"

def get_windchill(t, v):
    windchill = 13.127 + (0.6215*t) - 13.947*(v**0.16) + 0.486*t*(v**0.16)
    return windchill

def get_discomfort_level(t, rh):
    hot = (1.8*t) - 0.55*(1-rh)*((1.8*t)-26) + 32
    return_list = ["low", "normal", "high", "very high"]
    if hot < 68:
        return return_list.index("low")
    elif hot < 75:
        return return_list.index("normal")
    elif hot < 80:
        return return_list.index("high")
    else:
        return return_list.index("very high")

def check_abnormal(t, month):
    if month >= 3 and month <= 5:
        return t < 5.0
    elif month >= 6 and month <= 8:
        return t > 28.0
    else:
        return t < -5.0
    
def normalization(month, ta, ws, hm, cloud, rain, snow):
    res = {}
    
    res['ab_t'] = check_abnormal(ta, month)
    res['heat'] = is_heat_wave = ta > 33.0
    res['snow'] = snow > 0
    res['rain'] = rain > 0
    
    res['discomfort'] = get_discomfort_level(ta, hm/100)
    res['cloudy'] = get_cloud_level(cloud)
    
    res['windchill'] = "%.2f" % get_windchill(ta, ws)
    
    return res 
    
def weather_request(date):
    URL = "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
    date = {
        'ServiceKey':key,
        'pageNo':1,
        'numOfRows':24,
        'dataType':'JSON',
        'dataCd':'ASOS',
        'dateCd':'HR',
        'startDt':date,
        'startHh':'07',
        'endDt':date,
        'endHh':'21',
        'stnIds':98 # 경기도 동두천 98
    }

    res = req.get(URL, params=date)
    weather_dict = json.loads(res.text)
    return weather_dict['response']['body']['items']['item']
    
def get_normal_data(date):
    res = {"date":date}
    dummy = weather_request(date)
    breakfast = normalization(*get_weather_data(dummy, 7, 10))
    lunch = normalization(*get_weather_data(dummy, 11, 23))
    dinner = normalization(*get_weather_data(dummy, 17, 20))
    res['body'] = {
        'breakfast':breakfast,
        'lunch':lunch,
        'dinner':dinner
    }
    return res

def get_month_data(year, month):
    month_data = {"month":month}
    prefix = str(year) + "%02d" % month
    days_data = {}
    day_n = monthrange(year, month)
    for day in range(1,day_n[1]+1):
        date = prefix+"%02d" % day
        days_data[date] = get_normal_data(date)
    month_data["body"] = days_data
    return month_data

def down_data(target_date:str):
    date, h = target_date.split() # 20201025 11
    # 해당 시 40분 이후에야 해당 시 조회가능 점 예외처리 ㄱ
    URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtNcst"
    date = {
        'serviceKey':key,
        'pageNo':1,
        'numOfRows':24,
        'dataType':'JSON',
        'base_date':date,
        'base_time':'%02d' % int(h)+'00',
        'nx':55,
        'ny':76
    }
    res = req.get(URL, params=date)
    weather_dict = json.loads(res.text)
    dummy = weather_dict['response']['body']['items']['item']
    return {d['category']:d['obsrValue'] for d in dummy}

def get_forecast_data(date, h):
    app.logger.info("{0}/{1}".format(date, h))
    now = datetime.now()
    now_date, now_h, now_m = map(int, now.strftime("%Y%m%d %H %M").split())
    
    if now_m < 45:
        now_h -= 1
    app.logger.info("{0}_{1}_{2}".format(now_date, now_h, now_m))
    key = "wLCpJQcQ2vdq196iNT+iGP9wkMsqhsYisGcoPh2sOeTeOwm9VbizISvbdsMX5yhioQioPC+p3Qku1xLzD0UlyQ=="
    URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst"
    params = {
        'serviceKey':key,
        'pageNo':1,
        'numOfRows':220,
        'dataType':'JSON',
        'base_date':str(now_date), 
        'base_time':"%2d" % now_h + "00",
        'nx':55,
        'ny':76
    }
    res = req.get(URL, params=params)
    weather_dict = json.loads(res.text)
    rows = [d for d in weather_dict["response"]["body"]["items"]["item"] if d["fcstDate"] == date and d["fcstTime"] == h]
    fc_dict = {r["category"]:r["fcstValue"] for r in rows}
    return fc_dict

def basic_parse(target_date, kma_dict):
    date, h = target_date.split() # 20201025 11
    parse_data = {}
    app.logger.info(json.dumps(kma_dict))
    rs_code = rs[int(kma_dict["PTY"])]
    parse_data["rain"] = parse_data["snow"] = 0
    if rs_code == "Both":
        parse_data["rain"] = parse_data["snow"] = 1
    elif rs_code == "None":
        pass
    else:
        parse_data[rs_code.lower()] = 1
    parse_data["date"] = date
    parse_data["h"] = int(h)
    if "T1H" in kma_dict:
        parse_data["t"] = kma_dict["T1H"]
    else:
        parse_data["t"] = kma_dict["T3H"]
    parse_data["hm"] = kma_dict["REH"]
    parse_data["ws"] = kma_dict["WSD"]
    return parse_data

def get_weather(date_id):
    m = get_month(date_id)
    parse_data = get_weather_data(date_id)
    res = {}

    res['ab_t'] = int(check_abnormal(parse_data["t"], m))
    res['heat'] = int(parse_data["t"] > 33.0)
    res['snow'] = parse_data["snow"]
    res['rain'] = parse_data["rain"]
    res['discomfort'] = get_discomfort_level(parse_data["t"], parse_data["hm"]/100)
    res['windchill'] = "%.2f" % get_windchill(parse_data["t"], parse_data["ws"])

    return res

def get_forecast(date_id):
    m = get_month(date_id)
    date, mealtime = parse_date_id(date_id)
    # 12시간 뒤 데이터까지 나옴 , 관련하여 예외처리
    lookup = {"breakfast":"0900", "lunch":"1200", "dinner":"1800"}
    target_date = date.strftime("%Y%m%d") + " " + str(int(lookup[mealtime][:2]))
    app.logger.info(target_date)
    parse_data = basic_parse(target_date, get_forecast_data(date.strftime("%Y%m%d"), lookup[mealtime]))
    res = {}

    res['ab_t'] = int(check_abnormal(parse_data["t"], m))
    res['heat'] = int(parse_data["t"] > 33.0)
    res['snow'] = parse_data["snow"]
    res['rain'] = parse_data["rain"]
    res['discomfort'] = get_discomfort_level(parse_data["t"], parse_data["hm"]/100)
    res['windchill'] = "%.2f" % get_windchill(parse_data["t"], parse_data["ws"])

    return res  