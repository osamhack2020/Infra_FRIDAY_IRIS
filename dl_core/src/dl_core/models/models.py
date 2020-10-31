# coding: utf-8
from dl_core import db
import sqlalchemy.exc as SA
def init_db():
    db.create_all()
def _already_exist(db_model, obj, data):
    row = db.session.using_bind("slave").query(db_model).filter(obj == data).first()
    if row:
        return True
    else:
        return False

def already_exist(db_model, obj, data):
    return run_query(_already_exist, (db_model, obj, data))

# Lost connection 문제를 해결하기 위해 exception시 자동으로 다시 시도 구현
# attempts 수치를 조절할 필요는 있다.
def run_query(f, params=(), attempts=4, slave=False):
    while attempts > 0:
        attempts -= 1
        try:
            # "break" if query was successful and return any results
            return f(*params) 
        except SA.DBAPIError as exc:
            if attempts > 0 and exc.connection_invalidated:
                if not slave:
                    db.session.using_bind("master").rollback()
                else:
                    db.session.using_bind("slave").rollback()
            else:
                raise

t_daily_eat_log = db.Table(
    'daily_eat_log',
    db.Column('date_id', db.ForeignKey('date_mealtime_mapping.id', ondelete='RESTRICT', onupdate='RESTRICT'), primary_key=True, info='날짜 인덱스'),
    db.Column('member_id', db.ForeignKey('group_member_info.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True, info='구성원 고유 번호 [ 예) 군번 / 순번 ]')
)

t_daily_menu = db.Table(
    'daily_menu',
    db.Column('date_id', db.ForeignKey('date_mealtime_mapping.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True, info='날짜 인덱스'),
    db.Column('cafeteria_id', db.ForeignKey('cafeteria_list.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, info='식당 인덱스'),
    db.Column('menu_id', db.ForeignKey('menu_info.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, info='메뉴 인덱스')
)
class RealHeadcount(db.Model):
    __tablename__ = 'real_headcount'
    id = db.Column(db.Integer, primary_key=True, info='데이터 인덱스')
    date_id = db.Column(db.ForeignKey('date_mealtime_mapping.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, info='날짜 인덱스')
    n = db.Column(db.Integer, nullable=False, info="실 식수인원 수")

class DailyWeather(db.Model):

    __tablename__ = 'daily_weather'
    id = db.Column(db.Integer, primary_key=True, info='데이터 인덱스')
    date = db.Column(db.Date, nullable=False, info='날짜(20200101)')
    h = db.Column(db.Integer, nullable=False)
    t = db.Column(db.Float, nullable=False)
    hm = db.Column(db.Integer, nullable=False)
    ws = db.Column(db.Float, nullable=False)
    rain = db.Column(db.Boolean, nullable=False, info='비')
    snow = db.Column(db.Boolean, nullable=False, info='눈')

class FitData(db.Model):
    __tablename__ = 'fit_data'
    id = db.Column(db.Integer, primary_key=True, info='데이터 인덱스')
    serial = db.Column(db.Text, nullable=False)
    token_len = db.Column(db.Integer, nullable=False)

class MenuInfo(db.Model):
    __tablename__ = 'menu_info'

    id = db.Column(db.Integer, primary_key=True, info='메뉴 인덱스')
    menu_name = db.Column(db.String(45), nullable=False, info='메뉴 이름')
    info_serial = db.Column(db.Text, nullable=False, info='예) "구이류,튀김류" 이런 방식으로 데이터 저장')

class DateMealtimeMapping(db.Model):
    __tablename__ = 'date_mealtime_mapping'

    id = db.Column(db.Integer, primary_key=True, info='인덱스')
    korean_date = db.Column(db.Date, nullable=False, info='날짜(20200101)')
    meal_time = db.Column(db.Enum('breakfast', 'lunch', 'dinner'), nullable=False, info='식사시간 ( 1~3 : 아침, 점심, 저녁 )')

class DailyHeadcount(DateMealtimeMapping):
    __tablename__ = 'daily_headcount'

    date_id = db.Column(db.ForeignKey('date_mealtime_mapping.id', ondelete='RESTRICT', onupdate='RESTRICT'), primary_key=True, info='날짜 인덱스')
    official_count = db.Column(db.SmallInteger, nullable=False, info='식사 가능 인원 수')
    real_count = db.Column(db.SmallInteger, info='실제 식사 인원 수')

class DailyHolidayCheck(DateMealtimeMapping):
    __tablename__ = 'daily_holiday_check'

    date_id = db.Column(db.ForeignKey('date_mealtime_mapping.id', ondelete='RESTRICT', onupdate='RESTRICT'), primary_key=True, info='날짜 인덱스')
    is_weekend = db.Column(db.Boolean, nullable=False, info='휴일 여부')
    before_weekend = db.Column(db.Boolean, nullable=False, info='휴일 전날 여부')
    after_weekend = db.Column(db.Boolean, nullable=False, info='휴일 다음날 여부')
    before_long_weekend = db.Column(db.Boolean, nullable=False, info='연휴 ( 3일 이상 ) 전날 여부')
    after_long_weekend = db.Column(db.Boolean, nullable=False, info='연휴 ( 3일 이상 ) 다음날 여부')
    in_end_year = db.Column(db.Boolean, nullable=False, info='연말 ( 12 /  21~31 ) 여부')

class GroupList(db.Model):
    __tablename__ = 'group_list'

    id = db.Column(db.Integer, primary_key=True, info='인덱스')
    name = db.Column(db.String(45), nullable=False, unique=True, info='집단 이름')
    cafeteria_id = db.Column(db.ForeignKey('cafeteria_list.id', ondelete='RESTRICT', onupdate='RESTRICT'), index=True, info='배식소 인덱스')

class GroupMemberInfo(db.Model):
    __tablename__ = 'group_member_info'

    id = db.Column(db.Integer, primary_key=True, info='인덱스')
    member_id = db.Column(db.String(45), nullable=False, info='구성원 고유 번호 [ 예) 군번 / 순번 ]')
    group_id = db.Column(db.ForeignKey('group_list.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True, info='집단 인덱스')
    name = db.Column(db.String(15), nullable=False, info='이름')

    group = db.relationship('GroupList', primaryjoin='GroupMemberInfo.group_id == GroupList.id', backref='group_member_infos')

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True, info='인덱스')
    chat_id = db.Column(db.Integer, unique=True, info='ID역할을 할 chat_id')
    name = db.Column(db.String(45), nullable=False, info='멤버 이름')
    cafeteria = db.Column(db.String(45), nullable=False, info='구내식당 이름 [ (군) 급양대 이름 ]')
    password = db.Column(db.String(128), nullable=False, info='비밀 번호 (sha3-512 해싱 예정 )')

class CafeteriaList(db.Model):
    __tablename__ = 'cafeteria_list'

    id = db.Column(db.Integer, primary_key=True, info='인덱스')
    name = db.Column(db.String(45), nullable=False, info='구내식당 이름 [ (군) 급양대 이름 ]')

class RegisterCode(db.Model):
    __tablename__ = 'register_code'
 
    id       = db.Column(db.Integer, primary_key=True)
    code     = db.Column(db.String(20), nullable=False, info='등록 코드')

class MemberChatIdMapping(db.Model):
    __tablename__ = 'member_chat_id_map'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.ForeignKey('group_member_info.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True, info='멤버 인덱스')
    chat_id = db.Column(db.Integer, nullable=False, info='채팅방 고유번호')