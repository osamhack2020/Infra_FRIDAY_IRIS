from dl_core import db
from dl_core.models.models import run_query, already_exist, t_daily_menu
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