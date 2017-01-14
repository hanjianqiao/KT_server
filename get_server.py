import os
import re
import random
import codecs
import hashlib
import sqlite3
import http.client
import json
import ssl
from flask import *
import datetime

app = Flask(__name__)

current_path = os.path.dirname(__file__)
database_folder = os.path.join(current_path, 'database')
if not os.path.exists(database_folder):
    os.mkdir(database_folder)
database_path = os.path.join(database_folder, 'user_info.db')


# headers
headers = {'Content-type': 'application/json'}

def register(userid, password, code, email, qq, wechat, taobao):
    # create user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "password":password,
            "code":code,
            "email":email,
            "qq":qq,
            "wechat":wechat,
            "taobao":taobao}
    json_foo = json.dumps(foo)
    connection.request('POST', '/register', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def charge(userid, amount):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "amount":amount}
    json_foo = json.dumps(foo)
    connection.request('POST', '/charge', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def uplevel(userid):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid}
    json_foo = json.dumps(foo)
    connection.request('POST', '/uplevel', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def up2vip(userid, year, month, day, fee):
    # vip user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "expire_year":year,
            "expire_month":month,
            "expire_day":day,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/up2vip', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def extendvip(userid, extend_month, fee):
   # extend vip user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "extend_month":extend_month,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/extendvip', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def extendagent(userid, level, invitation, extend, fee):
    # agent user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "level":level,
            "invitation":invitation,
            "extend":extend,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/extendagent', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def secret_pass(secret):
    return hashlib.md5(secret.encode('utf-8')).hexdigest()


def secret_check(password, secret):
    return secret_pass(password) == secret


@app.route('/register', methods=['POST'])
def api_register():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')
        code = info_data.get('code', '')
        email = info_data.get('email', '')
        qq = info_data.get('qq', '')
        wechat = info_data.get('wechat', '')
        taobao = info_data.get('taobao', '')
        return register(user_id, password, code, email, qq, wechat, taobao)
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/query', methods=['GET'])
def api_query():
    info_data = request.get_json(force=True, silent=True)
    user_id = request.args.get('id')
    password = request.args.get('pwd')

    # format check
    if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
        return jsonify({'status': 'failed', 'message': 'user_id format error'})
    if not (isinstance(password, str) and len(password) >= 6):
        return jsonify({'status': 'failed', 'message': 'password format error'})

    # user_id exists check
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
    ret = c.fetchall()
    if not ret:
        return jsonify({'status': 'failed', 'message': 'user_id not exists'})
    if not secret_check(password, ret[0][1]):
        return jsonify({'status': 'failed', 'message': 'password not match'})
    inviter, code, email, qq, wechat, taobao, type, level, expire_year, expire_month, expire_day, balance, invitation_remain, extend_remain, invitee_total, invitee_vip, invitee_agent, team_total = ret[0][2:]

    c.execute("SELECT * FROM deal_info WHERE user_id=?", (user_id,))
    ret = c.fetchall()
    wait = ''
    if ret:
        wait = ret[0][3]
    else:
        wait = 'none'

    data = {'user_id': user_id, 'inviter': inviter, 'code': code,
            'email': email, 'qq': qq, 'wechat': wechat, 'taobao': taobao, 'type': type,
            'level': level, 'expire_year': expire_year, 'expire_month': expire_month,
            'expire_day': expire_day, 'balance': balance, 'invitation_remain': invitation_remain,
            'extend_remain': extend_remain, 'invitee_total': invitee_total, 'invitee_vip': invitee_vip,
            'invitee_agent': invitee_agent, 'team_total': team_total, 'wait': wait}
    return jsonify({'status': 'ok', 'message': 'login ok', 'data': data})


@app.route('/login', methods=['POST'])
def api_login():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if not secret_check(password, ret[0][1]):
            return jsonify({'status': 'failed', 'message': 'password not match'})
        inviter, code, email, qq, wechat, taobao, type, level, expire_year, expire_month, expire_day, balance, invitation_remain, extend_remain, invitee_total, invitee_vip, invitee_agent, team_total = ret[0][2:]

        c.execute("SELECT * FROM deal_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        wait = ''
        if ret:
            wait = ret[0][3]
        else:
            wait = 'none'

        data = {'user_id': user_id, 'inviter': inviter, 'code': code,
                'email': email, 'qq': qq, 'wechat': wechat, 'taobao': taobao, 'type': type,
                'level': level, 'expire_year': expire_year, 'expire_month': expire_month,
                'expire_day': expire_day, 'balance': balance, 'invitation_remain': invitation_remain,
                'extend_remain': extend_remain, 'invitee_total': invitee_total, 'invitee_vip': invitee_vip,
                'invitee_agent': invitee_agent, 'team_total': team_total, 'wait': wait}
        return jsonify({'status': 'ok', 'message': 'login ok', 'data': data})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/charge', methods=['POST'])
def api_charge():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if not secret_check(password, ret[0][1]):
            return jsonify({'status': 'failed', 'message': 'password not match'})

        return charge(user_id, '1000')
    return jsonify({'status': 'failed', 'message': 'json data format error'})


up2vipinfo = {
    'price':'198'
}


@app.route('/up2vipinfo', methods=['POST'])
def api_up2vipinfo():
    return jsonify(up2vipinfo)


@app.route('/up2vip', methods=['POST'])
def api_up2vip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if not secret_check(password, ret[0][1]):
            return jsonify({'status': 'failed', 'message': 'password not match'})
        
        c.execute("SELECT * FROM deal_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if ret:
            return jsonify({'status': 'failed', 'message': 'You have something undergo: ' + ret[0][3]})

        now = datetime.datetime.now()
        return up2vip(user_id, str(now.year + int(now.month/12)), str(now.month%12+1), str(now.day), up2vipinfo['price'])
    return jsonify({'status': 'failed', 'message': 'json data format error'})


extendvipinfo = {
    '1':{'month':'1', 'price':'198'},
    '2':{'month':'2', 'price':'300'},
    '3':{'month':'3', 'price':'400'},
    '4':{'month':'10', 'price':'1000'},
}


@app.route('/extendvipinfo', methods=['POST'])
def api_extendvipinfo():
    return jsonify(extendvipinfo)


@app.route('/extendvip', methods=['POST'])
def api_extendvip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')
        month = info_data.get('month', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if not secret_check(password, ret[0][1]):
            return jsonify({'status': 'failed', 'message': 'password not match'})

        c.execute("SELECT * FROM deal_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if ret:
            return jsonify({'status': 'failed', 'message': 'You have something undergo: ' + ret[0][3]})

        return extendvip(user_id, month, str(int(month)*89))
    return jsonify({'status': 'failed', 'message': 'json data format error'})


extendagentinfo = {
        '1':{
            'level':'level1',
            'invite':'10',
            'extend':'0',
            'price':'1380'
        },
        '2':{
            'level':'level1',
            'invite':'0',
            'extend':'10',
            'price':'590'
        },
        '3':{
            'level':'level2',
            'invite':'30',
            'extend':'0',
            'price':'3240'
        },
        '4':{
            'level':'level2',
            'invite':'0',
            'extend':'30',
            'price':'1470'
        },
        '5':{
            'level':'level3',
            'invite':'100',
            'extend':'0',
            'price':'8800'
        },
        '6':{
            'level':'level3',
            'invite':'0',
            'extend':'100',
            'price':'3900'
        },
        '7':{
            'level':'level4',
            'invite':'300',
            'extend':'0',
            'price':'21900'
        },
        '8':{
            'level':'level4',
            'invite':'0',
            'extend':'300',
            'price':'10200'
        },
        '9':{
            'level':'level5',
            'invite':'1000',
            'extend':'0',
            'price':'63000'
        },
        '10':{
            'level':'level5',
            'invite':'0',
            'extend':'1000',
            'price':'29000'
        },
        '11':{
            'level':'level6',
            'invite':'5000',
            'extend':'0',
            'price':'290000'
        },
        '12':{
            'level':'level6',
            'invite':'0',
            'extend':'5000',
            'price':'120000'
        }
    }


@app.route('/extendagentinfo', methods=['POST'])
def api_extendagentinfo():
    return jsonify(extendagentinfo)


@app.route('/extendagent', methods=['POST'])
def api_extendagent():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')
        combo = info_data.get('combo', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if not secret_check(password, ret[0][1]):
            return jsonify({'status': 'failed', 'message': 'password not match'})
        
        c.execute("SELECT * FROM deal_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if ret:
            return 'You have something undergo: ' + ret[0][3]

        return extendagent(user_id, extendagentinfo[combo]['level'], extendagentinfo[combo]['invite'], extendagentinfo[combo]['extend'], extendagentinfo[combo]['price'])
    return jsonify({'status': 'failed', 'message': 'json data format error'})


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=10000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
