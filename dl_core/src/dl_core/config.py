### DB Connecion ###
mysql_config = {
	'host': '172.20.1.2', # HA Proxy IP
	'user': 'dbmanager',
	'pass': 'iris',
	'db': 'friday'
}
RPORT = 3307
WPORT = 3306
def get_alchemy_uri():
    # Default : Write => For Migration
    return 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
            mysql_config['user'], mysql_config['pass'], mysql_config['host'], WPORT, mysql_config['db']
    )

SQLALCHEMY_BINDS = {
  'master': 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(mysql_config['user'], mysql_config['pass'], mysql_config['host'], WPORT, mysql_config['db']),
  'slave': 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(mysql_config['user'], mysql_config['pass'], mysql_config['host'], RPORT, mysql_config['db'])
}