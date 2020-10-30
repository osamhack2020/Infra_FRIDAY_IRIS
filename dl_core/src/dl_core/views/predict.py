import json
from flask import Blueprint
from datetime import datetime
from calendar import monthrange
from dl_core.models.predict import find_len, insert_fit_data, get_fit_data_list
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
# x = df[
#     [
#         "is_h",
#         "before_h",
#         "after_h",
#         "before_lh",
#         "after_lh",
#         "in_end",
#         "official_count",
#         "ab_t",
#         "heat",
#         "rain",
#         "snow",
#         "discomfort",
#         "cloudy",
#         "rice",
#         "porridge",
#         "bowl_or_soup_rice",
#         "mix_or_fri_rice",
#         "gimbap_or_sushi",
#         "noodle",
#         "curry_or_black-soybean",
#         "burger",
#         "soup",
#         "stew",
#         "roast",
#         "mix",
#         "fire_mix",
#         "pickle",
#         "pancake",
#         "boil_down",
#         "steam",
#         "fried",
#         "salad",
#         "wrap",
#         "tofu",
#         'product',
#         'milk',
#         'snack_or_bread',
#         'drink',
#         "grain",
#         "bean",
#         "egg",
#         "muk",
#         "fish",
#         "meat",
#         "vegetable",
#         "seaweed",
#         "rice_cake",
#         "source_or_paste",
#         "kimchi",
#         "dumpling",
#         "fruit",
#         "sagol"
#     ]
# ]
# y = df[['real_headcount']]
# x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, test_size=0.2)
# 모델 생성
# mlr = LinearRegression()
# mlr.fit(x_train, y_train) 
# 예측에 필요한 소스  입력
# my_apartment = [[1, 1, 620, 16, 1, 98, 1, 0, 1, 0, 0, 1, 1, 0]]
# my_predict = mlr.predict(my_apartment)
serial_keys = [
    "additional_h", # 추가적인 휴일 ( 전투 휴무 등 )
    "is_h",
    "before_h",
    "after_h",
    "before_lh",
    "after_lh",
    "in_end",
    "official_count",
    "ab_t",
    "heat",
    "rain",
    "snow",
    "discomfort",
    "cloudy",
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

@predict.route('/', methods=['GET'])
def _predict():
    # len 이 똑같아야 하니까 기준은 아마 date_mealtime_mapping 얘가 될듯
    # sample 하나 이상 필요
    if get_fit_len < 2:
        return json.dumps({"status":"error", "msg":"딥러닝에 쓸 데이터가 부족합니다"})
    fit_data_list = get_fit_data_list()
    today = datetime.today().strftime("%Y%m%d")
    day_info, _ = check_day_full(today)
    
    return day_info, 200

