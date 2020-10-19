### DB Connecion ###
mysql_config = {
	'host': '172.20.1.2', # HA Proxy IP
	'user': 'dbmanager',
	'pass': 'iris',
	'db': 'friday'
}

def get_alchemy_uri(mode='read'):
    // TODO: 3307 / 3306 으로 분기 시킬 방안 구상
    // 1. rodb / rwdb
    // 2. 실시간으로 uri만 바꾸는 방법이 있을까?
    port = 3306 if mode == 'read' else 3306 
    return 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
            mysql_config['user'], mysql_config['pass'], mysql_config['host'], port, mysql_config['db']
    )