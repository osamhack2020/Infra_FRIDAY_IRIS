from dl_core import db
from dl_core.models.models import run_query, FitData, RealHeadcount, DateMealtimeMapping, MonthHoliday
from datetime import datetime
def get_fit_len() ->  int:
    len = db.session.using_bind("slave").query(FitData).count()
    if len:
        return len
    else:
        return -1

def find_len():
    l = run_query(get_fit_len)
    if l != -1:
        return l
    return -1

def _insert_fit_data(serial:str, token_len:int):
    new_sheet = FitData(serial=serial, token_len=token_len)
    sess = db.session.using_bind("master")
    sess.add(new_sheet)
    sess.commit()
    
def insert_fit_data(serial:str, token_len:int):
    run_query(_insert_fit_data, (serial, token_len))

def get_all_fit_data() ->  list:
    rows = db.session.using_bind("slave").query(FitData).all()
    if row:
        l = [ r.serial for r in rows ]
        return l
    else:
        return []

def get_fit_data_list() -> list:
    l = run_query(get_all_fit_data)
    if l:
        return l
    else:
        return []

def get_all_real_headcount():
    rows = db.session.using_bind("slave").query(RealHeadcount).all()
    if rows:
        l = [ r.date_id for r in rows ]
        return l
    else:
        return []

def get_real_headcount_list():
    l = run_query(get_all_real_headcount)
    if l:
        return l
    else:
        return []

def find_datestr_at_id(date_id):
    row = db.session.using_bind("slave").query(DateMealtimeMapping).filter_by(id=date_id).first()
    if row:
        return row.korean_date
    else:
        return ''

def get_datetime_from_id(date_id):
    return run_query(find_datestr_at_id, ([date_id]))

def _get_real_headcount(date_id):
    row = db.session.using_bind("slave").query(RealHeadcount).filter_by(date_id=date_id).first()
    if row:
        return row.n
    else:
        return -1

def get_real_headcount(date_id):
    n = run_query(_get_real_headcount, ([date_id]))
    if n != -1:
        return n

def _db_exist(y, m):
    cnt = db.session.using_bind("slave").query(MonthHoliday).filter_by(y=y, m=m).count()
    if cnt:
        return True
    else:
        return False

def db_exist(y, m):
    return run_query(_db_exist, (y, m))

def parse_holiday_table(y, m):
    row = db.session.using_bind("slave").query(MonthHoliday).filter_by(y=y, m=m).first()
    if row:
        return row.token_len, row.serial.split(",")
    else:
        return -1, []

def get_holiday_from_db(y ,m):
    ml, tbl = run_query(parse_holiday_table, (y, m))
    return ml, tbl

def push_holiday_tbl(serial, token_len, y, m):
    new_htbl = MonthHoliday(serial=serial, token_len=token_len, y=y, m=m)
    sess = db.session.using_bind("master")
    sess.add(new_htbl)
    sess.commit()
    
def insert_holiday_tbl(tbl, y, m):
    token_len = len(tbl)
    serial = ",".join(tbl)
    run_query(push_holiday_tbl, (serial, token_len, y, m))
