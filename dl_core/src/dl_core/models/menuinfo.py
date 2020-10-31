from dl_core import db
from dl_core.models.models import run_query, already_exist, t_daily_menu, MenuInfo
menu_map = {
    "밥":"rice",
    "죽":"porridge",
    "덮밥국밥류":"bowl_or_soup_rice",
    "비빔밥볶음밥류":"mix_or_fri_rice",
    "김밥/초밥류":"gimbap_or_sushi",
    "국수류":"noodle",
    "면류":"noodle",
    "카레/짜장류":"curry_or_black-soybean",
    "햄버거류":"burger",
    "국탕류":"soup",
    "찌개류":"stew",
    "구이류":"roast",
    "무침류":"mix",
    "볶음류":"fire_mix",
    "장아찌류":"pickle",
    "전류":"pancake",
    "조림류":"boil_down",
    "찜류":"steam",
    "튀김류":"fried",
    "샐러드류":"salad",
    "쌈채소류":"wrap",
    "두부류":"tofu",
    "단품류":'product',
    "유제품":'milk',
    "빵과자류":'snack_or_bread',
    "음료및주류":'drink',
    "곡류":"grain",
    "두류":"bean",
    "난류":"egg",
    "묵류":"muk",
    "어패류":"fish",
    "육류":"meat",
    "채소류":"vegetable",
    "해조류":"seaweed",
    "떡류":"rice_cake",
    "양념 및 장류":"source_or_paste",
    "김치류":"kimchi",
    "만두류":"dumpling",
    "과일류":"fruit",
    "사골":"sagol",
}
def _get_menu(date_id):
    menu_len = db.session.using_bind("slave").query(t_daily_menu).filter_by(date_id=date_id).count()
    if menu_len:
        return menu_len
    else:
        return -1

def get_menu(date_id):
    l = run_query(_get_menu, ([date_id]))
    if l:
        return l
    else:
        return -1

def exist_menu(date_id):
    if get_menu(date_id) != -1:
        return True
    return False

def _get_menu_at_id(date_id, c_id):
    rows = db.session.using_bind("slave").query(t_daily_menu).filter_by(date_id=date_id, cafeteria_id=c_id).all()
    if rows:
        return [r.menu_id for r in rows]
    else:
        return []

def get_menu_at_id(date_id, c_id):
    l = run_query(_get_menu_at_id, (date_id, c_id))
    if l:
        return l

def get_serial(menu_id):
    row = db.session.using_bind("slave").query(MenuInfo).filter_by(id=menu_id).first()
    if row:
        return row.info_serial
    else:
        return ''

def get_menu_info(menu_id):
    res = {}
    serial = run_query(get_serial,([menu_id]))
    if serial:
        menu_infos = serial.split(",")
        for info in menu_infos:
            res[menu_map[info]] = 1
    return res