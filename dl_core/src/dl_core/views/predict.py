import json
from flask import Blueprint, request
from datetime import datetime
from calendar import monthrange
from dl_core.models.predict import find_len, insert_fit_data, get_fit_data_list, get_real_headcount_list, get_datetime_from_id, get_real_headcount
from dl_core.models.kma import exist_weather
from dl_core.views.kasi import check_holiday_full
from dl_core.views.kma import get_weather, get_forecast
from dl_core.models.menuinfo import exist_menu, get_menu_at_id, get_menu_info
from dl_core.secret import key
from dl_core.views.holiday import check_day_full
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# form = a:[] 형태 임 그럼 a 가 위 0 , 1, 이 옆이 됨
# is_h	before_h	after_h	before_lh	after_lh	in_end
# 휴일 , 휴일 전 , 휴일 후 , 연휴 전 , 연휴 후 , 연말 
# ab_t, heat, rain, snow, discomfort, cloudy, windchill
# 이상기온  폭염    비      눈       불퀘지수     구름    체감온도
# 밥, 죽, 덮밥국밥류, 비빔밥볶음밥류, 김밥/초밥류, 국수류, 카레/짜장류, 햄버거류, 국탕류, 찌개류, 구이류
# rice, porridge, bowl_or_soup_rice, mix_or_fri_rice, gimbap_or_sushi, noodle, curry_or_black-soybean, burger, soup, stew, roast
# 무침류, 볶음류, 장아찌류, 전류, 조림류, 찜류, 튀김류, 샐러드류, 쌈채소류, 두부류
# mix, fire_mix, pickle, pancake, boil_down, steam, fried, salad, wrap, tofu
# 단품류, 유제품, 빵과자류, 음료및주류
# product, milk, snack_or_bread, drink
# 곡류, 두류, 난류, 묵류, 어패류, 육류, 채소류, 해조류, 떡류, 양념 및 장류, 김치류, 만두류, 과일류, 사골
# grain, bean, egg, muk, fish, meat, vegetable, seaweed, rice_cake, source_or_paste, kimchi, dumpling, fruit, sagol
# 잔반량 데이터
serial_keys = [
    "is_h",
    "before_h",
    "after_h",
    "before_lh",
    "after_lh",
    "in_end",
    "ab_t",
    "heat",
    "rain",
    "snow",
    "discomfort",
    "windchill",
    "rice",
    "porridge",
    "bowl_or_soup_rice",
    "mix_or_fri_rice",
    "gimbap_or_sushi",
    "noodle",
    "curry_or_black-soybean",
    "burger",
    "soup",
    "stew",
    "roast",
    "mix",
    "fire_mix",
    "pickle",
    "pancake",
    "boil_down",
    "steam",
    "fried",
    "salad",
    "wrap",
    "tofu",
    'product',
    'milk',
    'snack_or_bread',
    'drink',
    "grain",
    "bean",
    "egg",
    "muk",
    "fish",
    "meat",
    "vegetable",
    "seaweed",
    "rice_cake",
    "source_or_paste",
    "kimchi",
    "dumpling",
    "fruit",
    "sagol",
    "official_count",
    "real_headcount"
]
predict = Blueprint('predict', __name__, url_prefix='/predict')
def get_fit_len():
    # 쌓인 데이터 길이
    fit_len = find_len()
    return fit_len

def serialize(fit_data_dict):
    sorted_list = []
    for k in serial_keys:
        sorted_list.append(fit_data_dict[k])
    return ",".join(sorted_list)

def unserialize(serial):
    fit_data_dict = {}
    tokens = serial.split(",")
    for i, k in enumerate(serial_keys):
        fit_data_dict[k] = tokens[i]
    return fit_data_dict

def push_fit_data():
    token_len = len(serial_keys)
    serial = serialize(fit_data_dict)
    insert_fit_data(serial, token_len)

def get_fitable_len():
    l = get_real_headcount_list()
    count = 0
    for date_id in l:
        if exist_weather(date_id):
            if exist_menu(date_id):
                count += 1
    return count

@predict.route('/', methods=['GET'])
def _predict():
    pd_id = request.args.get("pd_id") # 예측할 Date map id
    c_id = request.args.get("c_id") # cafeteria_id
    o_cnt = request.args.get("o_cnt") # official_count
    additional_h = request.args.get("additional_h") # 특수 휴일 여부 : 1, 0
    # len 이 똑같아야 하니까 기준은 아마 date_mealtime_mapping 얘가 될듯
    # sample 하나 이상 필요
    fit_data_list = []
    init_list = []
    if get_fit_len() < 2 and get_fitable_len() < 2:
            return json.dumps({"status":"error", "msg":"딥러닝에 쓸 데이터가 부족합니다"}, ensure_ascii=False), 200
    if get_fit_len() >= 2:
        fit_data_list = get_fit_data_list()
        fit_data_list = [unserialize(s) for s in fit_data_list]
    elif get_fitable_len() >= 2:
        req_len = get_fitable_len()
        init_list = [{k:0 for k in serial_keys} for _ in range(req_len)]
        l = get_real_headcount_list()
        for i, date_id in enumerate(l):
            dt = get_datetime_from_id(date_id)
            if dt:
                hdata = check_holiday_full(dt)
                init_list[i].update(hdata)
            wdata = get_weather(date_id)
            init_list[i].update(wdata)
            menu_data = get_menu_at_id(date_id, c_id)
            for mid in menu_data:
                init_list[i].update(get_menu_info(mid))
            init_list[i]["real_headcount"] = get_real_headcount(date_id)
    fit_data_list.extend(init_list)
    full_row = pd.DataFrame()
    for fit_dict in fit_data_list:
        row = pd.DataFrame.from_dict(fit_dict, orient="index").T
        full_row = full_row.append(row)

    x = full_row[[
        "is_h",
        "before_h",
        "after_h",
        "before_lh",
        "after_lh",
        "in_end",
        "ab_t",
        "heat",
        "rain",
        "snow",
        "discomfort",
        "rice",
        "porridge",
        "bowl_or_soup_rice",
        "mix_or_fri_rice",
        "gimbap_or_sushi",
        "noodle",
        "curry_or_black-soybean",
        "burger",
        "soup",
        "stew",
        "roast",
        "mix",
        "fire_mix",
        "pickle",
        "pancake",
        "boil_down",
        "steam",
        "fried",
        "salad",
        "wrap",
        "tofu",
        'product',
        'milk',
        'snack_or_bread',
        'drink',
        "grain",
        "bean",
        "egg",
        "muk",
        "fish",
        "meat",
        "vegetable",
        "seaweed",
        "rice_cake",
        "source_or_paste",
        "kimchi",
        "dumpling",
        "fruit",
        "sagol",
        "official_count"
    ]]
    y = full_row[['real_headcount']]
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2)

    mlr = LinearRegression()
    mlr.fit(x_train, y_train) 
    init_dict = {k:0 for k in serial_keys}
    dt = get_datetime_from_id(pd_id)
    if dt:
	    hdata = check_holiday_full(dt)
	    init_dict.update(hdata)
    wdata = get_forecast(pd_id)
    init_dict.update(wdata)
    menu_data = get_menu_at_id(pd_id, c_id)
    for mid in menu_data:
	    init_dict.update(get_menu_info(mid))
    init_dict.pop("real_headcount")
    src = [init_dict.values()]
    my_predict = mlr.predict(src)
    return json.dumps({"status":"ok", "msg":"예상 인원 : {}".format(my_predict)}, ensure_ascii=False), 200

