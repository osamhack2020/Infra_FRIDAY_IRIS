from calendar import monthrange
from datetime import datetime
import json
import requests as req
from dl_core.secret import key

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
    if hot < 68:
        return "low"
    elif hot < 75:
        return "normal"
    elif hot < 80:
        return "high"
    else:
        return "very high"

def check_abnormal(t, month):
    if month >= 3 and month <= 5:
        return t < 5.0
    elif month >= 6 and month <= 8:
        return t > 28.0
    else:
        return t < -5.0
        
def get_weather_data(hours, st, en):
    ta = ws = hm = 0
    cloud = rain = snow = 0
    month = int(hours[0]['tm'][5:7])
    for h in hours:
        hour = int(h['tm'].split(':')[0].split()[1])
        if hour >= st and hour <=en:
            ta += float(h['ta'])
            ws += float(h['ws'])
            hm += float(h['hm'])
            cloud += float(h['dc10Tca'] if h['dc10Tca'] else 0)
            rain += float(h['rn'] if h['rn'] else 0)
            snow += float(h['dsnw'] if h['dsnw'] else 0)
    cnt = en-st+1
    ta /= cnt
    ws /= cnt
    hm /= cnt
    cloud /= cnt
    rain /= cnt
    snow /= cnt
    return (month, ta, ws, hm, cloud, rain, snow)
    
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

def basic_parse(target_date, kma_dict):
    date, h = target_date.split() # 20201025 11
    parse_data = {}
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
    parse_data["t"] = kma_dict["T1H"]
    parse_data["hm"] = kma_dict["REH"]
    parse_data["ws"] = kma_dict["WSD"]
    return parse_data