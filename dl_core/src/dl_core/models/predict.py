from dl_core import db
from dl_core.models.models import run_query, FitData
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