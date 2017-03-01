# -*- coding: utf-8 -*-
import os
import re
import random
import codecs
import hashlib
import sqlite3
from flask import *
import datetime
import ast
import ssl
import http.client
import sys

app = Flask(__name__)

current_path = os.path.dirname(__file__)
database_folder = os.path.join(current_path, 'database')
if not os.path.exists(database_folder):
    os.mkdir(database_folder)
database_path = os.path.join(database_folder, 'user_info.db')

# headers
headers = {'Content-type': 'application/json'}

def mes2user(userid, title, body):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 30000, context = context)
    foo = {  'userid': userid,
        'title':title,
        'body':body}
    json_foo = json.dumps(foo)
    connection.request('POST', '/add', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret

def mes2bil(userid, action, amount):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 40000, context = context)
    foo = {  'userid': userid,
        'action':action,
        'amount':amount}
    json_foo = json.dumps(foo)
    connection.request('POST', '/add', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    return ret


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)

        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = c.fetchall()
        if not table_list:
            c.execute("CREATE TABLE role ( id INTEGER NOT NULL, name VARCHAR(80), description VARCHAR(255), PRIMARY KEY (id), UNIQUE (name) )")
            c.execute("CREATE TABLE roles_users ( user_id INTEGER, role_id INTEGER, FOREIGN KEY(user_id) REFERENCES user (id), FOREIGN KEY(role_id) REFERENCES role (id) )")
            c.execute("CREATE TABLE user ( id INTEGER NOT NULL, first_name VARCHAR(255), last_name VARCHAR(255), email VARCHAR(255), password VARCHAR(255), active BOOLEAN, confirmed_at DATETIME, PRIMARY KEY (id), UNIQUE (email), CHECK (active IN (0, 1)) )")
            c.execute("""
                CREATE TABLE user_info (user_id TEXT,
                                        password TEXT,
                                        inviter TEXT,
                                        code TEXT,
                                        email TEXT,
                                        qq TEXT,
                                        wechat TEXT,
                                        taobao TEXT,
                                        type TEXT,
                                        level TEXT,
                                        expire_year TEXT,
                                        expire_month TEXT,
                                        expire_day TEXT,
                                        balance TEXT,
                                        invitation_remain TEXT,
                                        extend_remain TEXT,
                                        invitee_total TEXT,
                                        invitee_vip TEXT,
                                        invitee_agent TEXT,
                                        team_total TEXT)
                """)
            c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      ('13800000000', 'system', '13800000000', '100000',
                       'admin@kouchenvip.com', '88888888', 'kouchenadmin', 'kouchenadmin', 'agent',
                       'system', '2200', '01', '01', '0', '10000', '100000', '0', '0', '0', '0'))
            c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      ('13900000000', 'intivation', '13800000000', '100000',
                       'admin@kouchenvip.com', '88888888', 'kouchenadmin', 'kouchenadmin', 'agent',
                       'system', '100001', '01', '01', '0', '10000', '100000', '0', '0', '0', '0'))
            c.execute("""
                CREATE TABLE deal_info (deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id TEXT,
                                        inviter_id TEXT,
                                        type TEXT,
                                        need_invite TEXT,
                                        need_extend TEXT,
                                        fee TEXT,
                                        end_year TEXT,
                                        end_month TEXT,
                                        end_day TEXT,
                                        end_hour TEXT,
                                        end_minute TEXT,
                                        interval TEXT)
                """)
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


def api_uplevel(user_id):
    c = get_db().cursor()

    # user info
    c.execute("SELECT inviter, level FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    level = inviter_row[0][1]

    # inviter and top inviter info
    c.execute("SELECT inviter, invitee_total, invitee_vip, invitee_agent FROM user_info WHERE user_id = ?", (inviter,))
    inviter_row = c.fetchall()
    if inviter_row[0][0] == inviter:
        return jsonify({'status': 'falied', 'message': 'You\'re under the system, no upgrading'})
    top_inviter = inviter_row[0][0]
    invitee_total = inviter_row[0][1]
    invitee_vip = inviter_row[0][2]
    invitee_agent = inviter_row[0][3]
    c.execute("SELECT inviter, invitee_total, invitee_vip, invitee_agent FROM user_info WHERE user_id = ?", (top_inviter,))
    inviter_row = c.fetchall()
    top_invitee_total = inviter_row[0][1]
    top_invitee_vip = inviter_row[0][2]
    top_invitee_agent = inviter_row[0][3]

    # count number change
    if level == 'user':
        invitee_total = str(int(invitee_total)-1)
        top_invitee_total = str(int(top_invitee_total)+1)
    elif level == 'vip':
        invitee_total = str(int(invitee_total)-1)
        top_invitee_total = str(int(top_invitee_total)+1)
        invitee_vip = str(int(invitee_vip)-1)
        top_invitee_vip = str(int(top_invitee_vip)+1)
    else:
        invitee_total = str(int(invitee_total)-1)
        top_invitee_total = str(int(top_invitee_total)+1)
        invitee_vip = str(int(invitee_vip)-1)
        top_invitee_vip = str(int(top_invitee_vip)+1)
        invitee_agent = str(int(invitee_agent)-1)
        top_invitee_agent = str(int(top_invitee_agent)+1)

    # update user inviter and top_inviter
    c.execute("UPDATE user_info SET inviter = ? WHERE user_id = ?",(top_inviter, user_id,))
    c.execute("UPDATE user_info SET invitee_total = ?, invitee_vip = ?, invitee_agent = ? WHERE user_id = ?",
        (invitee_total, invitee_vip, invitee_agent, inviter))
    c.execute("UPDATE user_info SET invitee_total = ?, invitee_vip = ?, invitee_agent = ? WHERE user_id = ?",
        (top_invitee_total, top_invitee_vip, top_invitee_agent, top_inviter))

    get_db().commit()
    mes2user(top_inviter, '获得转入邀请', user_id+'已成为您的下级')
    mes2user(user_id, '上级变更', '您的上级已变更为：'+top_inviter)
    mes2user(inviter, '失去下级', '您已失去下级：'+user_id)
    return jsonify({'status': 'ok', 'message': 'uplevel ok'})


@app.route('/registerbyid', methods=['POST'])
def api_registerbyid():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')
        inviter = info_data.get('inviter', '')
        email = info_data.get('email', '')
        qq = info_data.get('qq', '')
        wechat = info_data.get('wechat', '')
        taobao = info_data.get('taobao', '')

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(inviter, str) and len(inviter) == 11 and all(map(lambda d: d.isdigit(), inviter))):
            return jsonify({'status': 'failed', 'message': 'inviter format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})
        if not (isinstance(email, str) and re.match(r'[^@]+@[^@]+\.[^@]+', email)):
            return jsonify({'status': 'failed', 'message': 'email format error'})

        c = get_db().cursor()

        # invitation code check
        c.execute("SELECT user_id FROM user_info WHERE user_id=?", (inviter,))
        inviter_row = c.fetchall()
        if not inviter_row:
            return jsonify({'status': 'failed', 'message': 'inviter not exist'})

        # user_id exists check
        c.execute("SELECT user_id FROM user_info WHERE user_id=?", (user_id,))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': 'user_id already exists'})

        # email exists check
        c.execute("SELECT email FROM user_info WHERE email=?", (email,))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': 'email already exists'})

        # register user, and update inviter's invitee_total by add 1
        secret = secret_pass(password)
        c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, secret, inviter, '000000', email, qq, wechat, taobao, 'user', 'user', '2017', '01', '01', '0', '0', '0', '0', '0', '0', '0'))
        c.execute("SELECT invitee_total FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchall()
        invitee_total = inviter_row[0][0]
        newValue = str(int(invitee_total)+1)
        c.execute("UPDATE user_info SET invitee_total = ? WHERE user_id = ?",(newValue, inviter,))

        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'register ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


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

        # format check
        if not (isinstance(user_id, str) and len(user_id) == 11 and all(map(lambda d: d.isdigit(), user_id))):
            return jsonify({'status': 'failed', 'message': '用户名格式错误'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})
        if not (isinstance(code, str) and len(code) == 6 and all(map(lambda d: d.isdigit(), code))):
            return jsonify({'status': 'failed', 'message': '邀请码格式错误'})
        #if not (isinstance(email, str) and re.match(r'[^@]+@[^@]+\.[^@]+', email)):
        #    return jsonify({'status': 'failed', 'message': '邮件格式错误'})

        c = get_db().cursor()

        # invitation code check
        c.execute("SELECT user_id FROM user_info WHERE code=?", (code,))
        inviter_row = c.fetchall()
        if not inviter_row:
            return jsonify({'status': 'failed', 'message': '邀请码不存在'})
        inviter = inviter_row[0][0]

        # user_id exists check
        c.execute("SELECT user_id FROM user_info WHERE user_id=?", (user_id,))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': '用户名已存在'})

        # email exists check
        #c.execute("SELECT email FROM user_info WHERE email=?", (email,))
        #if c.fetchall():
        #    return jsonify({'status': 'failed', 'message': '邮箱已被注册'})

        # register user, and update inviter's invitee_total by add 1
        secret = secret_pass(password)
        c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, secret, inviter, '000000', email, qq, wechat, taobao, 'user', 'user', '2017', '01', '01', '0', '0', '0', '0', '0', '0', '0'))
        c.execute("SELECT invitee_total FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchall()
        invitee_total = inviter_row[0][0]
        newValue = str(int(invitee_total)+1)
        c.execute("UPDATE user_info SET invitee_total = ? WHERE user_id = ?",(newValue, inviter,))
        get_db().commit()

        mes2user(user_id, '欢迎加入小牛快淘！', '欢迎加入快淘大家庭，如有任何疑问，请关注并咨询微信公众号“小牛快淘”，会有专业人员为您服务，我们更支持你的梦想！')
        mes2user(inviter, '邀请增加', '用户已通过您的邀请码进行注册：'+user_id)
        return jsonify({'status': 'ok', 'message': '注册成功'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


def up2vip(user_id, expire_year, expire_month, expire_day, fee, log):
    c = get_db().cursor()

    # check inviter's remains
    c.execute("SELECT inviter, balance, level FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    user_balance = inviter_row[0][1]
    user_level = inviter_row[0][2]
    if user_level != 'user':
        return jsonify({'status': 'failed', 'message': '你已经是VIP'})
    if int(user_balance) < int(fee):
        return jsonify({'status': 'failed', 'message': '余额不足'})
    c.execute("SELECT invitee_vip, invitation_remain, balance FROM user_info WHERE user_id = ?",(inviter,))
    inviter_row = c.fetchall()
    invitee_vip = inviter_row[0][0]
    invitation_remain = inviter_row[0][1]
    inviter_balance = inviter_row[0][2]
    if int(invitation_remain) < 1:
        if log == True:
            now = datetime.datetime.now()
            des_time = now + datetime.timedelta(hours=20)
            c.execute("INSERT INTO deal_info (user_id, inviter_id, type, need_invite, need_extend, fee, end_year, end_month, end_day, end_hour, end_minute, interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, inviter, 'up2vip', str(1), str(0), str(198), str(des_time.year), str(des_time.month), str(des_time.day), str(des_time.hour), str(des_time.minute), str(20)))
            get_db().commit()
            mes2user(inviter, '请增购套餐', '用户'+user_id+'需要升级VIP，您的剩余邀请已不足')
        return jsonify({'status': 'failed', 'message': '用户'+str(inviter)+'剩余VIP邀请不足'})
    invitee_vip = str(int(invitee_vip)+1)
    invitation_remain = str(int(invitation_remain)-1)
    user_balance = str(int(user_balance)-int(fee))
    inviter_balance = str(int(inviter_balance)+int(fee))

    # update user's infomation
    c.execute("SELECT expire_year FROM user_info WHERE user_id = 13900000000")
    inviter_row = c.fetchall()
    code = inviter_row[0][0]
    newValue = str(int(code)+1)
    c.execute("UPDATE user_info SET expire_year = ? WHERE user_id = 13900000000",(newValue,))
    c.execute("UPDATE user_info SET balance = ?, expire_year = ?, expire_month = ?, expire_day = ?, code = ?, type = ?, level = ? WHERE user_id = ?",
                                  (user_balance, expire_year, expire_month, expire_day, code, 'vip', 'vip', user_id,))

    # update inviter's information
    c.execute("UPDATE user_info SET balance = ?, invitee_vip = ?, invitation_remain = ? WHERE user_id = ?",
              (inviter_balance, invitee_vip, invitation_remain, inviter,))

    get_db().commit()
    mes2user(user_id, '恭喜升级VIP', '欢迎加入VIP，现在请使用佣金及优惠券查询功能')
    mes2user(inviter, '下级升级VIP', '您的下级已升级为VIP：'+user_id)
    mes2bil(user_id, '购买VIP', '-'+fee)
    mes2bil(inviter, '售出邀请名额', '+'+fee)
    return jsonify({'status': 'ok', 'message': '购买VIP成功'})


@app.route('/up2vip', methods=['POST'])
def api_up2vip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        expire_year = info_data.get('expire_year', '')
        expire_month = info_data.get('expire_month', '')
        expire_day = info_data.get('expire_day', '')
        fee = info_data.get('fee', '')

        return up2vip(user_id, expire_year, expire_month, expire_day, fee, True)

    return jsonify({'status': 'failed'})


def extendvip(user_id, extend_month, fee, log):
    c = get_db().cursor()

    # check inviter's remains
    c.execute("SELECT inviter, balance, level FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    user_balance = inviter_row[0][1]
    user_level = inviter_row[0][2]
    if user_level == 'user':
        return jsonify({'status': 'failed', 'message': 'Please upgrade to be a VIP first'})
    if int(user_balance) < int(fee):
        return jsonify({'status': 'failed', 'message': 'balance' + user_balance + ' ' + str(fee)})
    c.execute("SELECT extend_remain, balance FROM user_info WHERE user_id = ?",(inviter,))
    inviter_row = c.fetchall()
    extend_remain = inviter_row[0][0]
    inviter_balance = inviter_row[0][1]
    if int(extend_remain) < int(extend_month):
        if log == True:
            now = datetime.datetime.now()
            des_time = now + datetime.timedelta(hours=20)
            c.execute("INSERT INTO deal_info (user_id, inviter_id, type, need_invite, need_extend, fee, end_year, end_month, end_day, end_hour, end_minute, interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, inviter, 'extendvip', str(0), extend_month, fee, str(des_time.year), str(des_time.month), str(des_time.day), str(des_time.hour), str(des_time.minute), str(20)))
            get_db().commit()
            mes2user(inviter, '请增购套餐', '用户'+user_id+'需要延长VIP'+extend_month+'个月，您的剩余套餐已不足')
        return jsonify({'status': 'failed', 'message': '用户'+str(inviter)+'续费次数不足'})
    extend_remain = str(int(extend_remain)-int(extend_month))
    user_balance = str(int(user_balance)-int(fee))
    inviter_balance = str(int(inviter_balance)+int(fee))

    # update user's infomation
    c.execute("SELECT expire_year, expire_month FROM user_info WHERE user_id= ?", (user_id,))
    ret = c.fetchall()
    expire_year = str(int(int(ret[0][0])+(int(ret[0][1])-1+int(extend_month))/12))
    expire_month = str((int(ret[0][1])-1+int(extend_month))%12+1)
    c.execute("UPDATE user_info SET balance = ?, expire_year = ?, expire_month = ? WHERE user_id = ?",
                                  (user_balance, expire_year, expire_month, user_id,))

    # update inviter's information
    c.execute("UPDATE user_info SET balance = ?, extend_remain = ? WHERE user_id = ?",
              (inviter_balance, extend_remain, inviter,))

    get_db().commit()

    mes2user(user_id, '成功延长VIP', '您的VIP延长了'+extend_month+'个月')
    mes2user(inviter, '售出延长VIP', '您的下级VIP延长'+extend_month+'个月')
    mes2bil(user_id, 'VIP延长'+extend_month+'个月', '-'+fee)
    mes2bil(inviter, '售出VIP延长'+extend_month+'个月', '+'+fee)
    return jsonify({'status': 'ok', 'message': '续费成功'})


@app.route('/extendvip', methods=['POST'])
def api_extendvip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        extend_month = info_data.get('extend_month', '')
        fee = info_data.get('fee', '')

        return extendvip(user_id, extend_month, fee, True)
        
    return jsonify({'status': 'failed'})


def extendagent(user_id, level, invitation, extend, fee, log):
    c = get_db().cursor()
    # check inviter's remains
    c.execute("SELECT inviter, balance, level FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    user_balance = inviter_row[0][1]
    user_level = inviter_row[0][2]
    if user_level == 'user':
        return jsonify({'status': 'failed', 'message': "请先购买VIP"})
    if int(user_balance) < int(fee):
        return jsonify({'status': 'failed', 'message': str(user_id)+' balance:' + str(user_balance) + ' need:' + str(fee)})
    c.execute("SELECT invitee_agent, invitation_remain, extend_remain, balance FROM user_info WHERE user_id = ?",(inviter,))
    inviter_row = c.fetchall()
    invitee_agent = inviter_row[0][0]
    invitation_remain = inviter_row[0][1]
    extend_remain = inviter_row[0][2]
    inviter_balance = inviter_row[0][3]
    if int(invitation_remain) < int(invitation) or int(extend_remain) < int(extend):
        if log == True:
            now = datetime.datetime.now()
            des_time = now + datetime.timedelta(hours=20)
            c.execute("INSERT INTO deal_info (user_id, inviter_id, type, need_invite, need_extend, fee, end_year, end_month, end_day, end_hour, end_minute, interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, inviter, level, invitation, extend, fee, str(des_time.year), str(des_time.month), str(des_time.day), str(des_time.hour), str(des_time.minute), str(20)))
            get_db().commit()
            mes2user(inviter, '请增购套餐', '用户'+user_id+'需要增购套餐'+extend+'个续费，'+invitation+'个邀请，您的剩余套餐已不足')
        return jsonify({'status': 'failed', 'message': str(inviter)+' invitation_remain:'+str(invitation_remain)+' need:'+str(invitation) + '' + str(inviter)+' extend_remain:'+str(extend_remain)+' need:'+str(extend)})
    invitation_remain = str(int(invitation_remain)-int(invitation))
    extend_remain = str(int(extend_remain)-int(extend))
    user_balance = str(int(user_balance)-int(fee))
    inviter_balance = str(int(inviter_balance)+int(fee))

    # update user's infomation
    c.execute("SELECT invitation_remain, extend_remain, level FROM user_info WHERE user_id = ?",(user_id,))
    inviter_row = c.fetchall()
    user_invitation_remain = str(int(inviter_row[0][0])+int(invitation))
    user_extend_remain = str(int(inviter_row[0][1])+int(extend))
    user_level = inviter_row[0][2]
    if user_level == 'vip':
        invitee_agent = str(int(invitee_agent)+1)
    c.execute("UPDATE user_info SET invitation_remain = ?, extend_remain = ?, level = ?, balance = ? WHERE user_id = ?",
              (user_invitation_remain, user_extend_remain, level, user_balance, user_id))

    # update inviter's information
    c.execute("UPDATE user_info SET invitee_agent = ?, invitation_remain = ?, extend_remain = ?, balance = ? WHERE user_id = ?",
              (invitee_agent, invitation_remain, extend_remain, inviter_balance, inviter))

    get_db().commit()
    mes2user(user_id, '新增套餐', '增加邀请次数：' + invitation + '次\n' + '增加续费次数：' + extend + '次')
    mes2user(inviter, '售出套餐', '售出邀请次数：' + invitation + '次\n' + '售出续费次数：' + extend + '次')
    mes2bil(user_id, '购买套餐', '-'+fee)
    mes2bil(inviter, '售出套餐', '+'+fee)
    return jsonify({'status': 'ok', 'message': '套餐购买成功'})

@app.route('/extendagent', methods=['POST'])
def api_extendagent():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        level = info_data.get('level', '')
        invitation = info_data.get('invitation', '')
        extend = info_data.get('extend', '')
        fee = info_data.get('fee', '')

        return extendagent(user_id, level, invitation, extend, fee, True)
        
    return jsonify({'status': 'failed'})


@app.route('/charge', methods=['POST'])
def charge():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        amount = info_data.get('amount', '')

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': '用户名不存在'})
        c.execute("SELECT balance FROM user_info WHERE user_id = ?", (user_id,))
        inviter_row = c.fetchall()
        balance = inviter_row[0][0]
        newValue = str(int(balance)+int(amount))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",(newValue, user_id,))
        get_db().commit()
        mes2user(user_id, '充值成功', '充值金额：'+amount+'元')
        mes2bil(user_id, '充值', '+'+amount)
    return jsonify({'status': 'ok', 'message': newValue})

@app.route('/drawback', methods=['POST'])
def drawback():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        amount = info_data.get('amount', '')

        # user_id exists check
        c = get_db().cursor()
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': '用户名不存在'})
        c.execute("SELECT balance FROM user_info WHERE user_id = ?", (user_id,))
        inviter_row = c.fetchall()
        balance = inviter_row[0][0]
        if(int(balance)<int(amount)):
            return jsonify({'status': 'failed', 'message': '余额不足'})
        newValue = str(int(balance)-int(amount))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",(newValue, user_id,))
        get_db().commit()
        mes2user(user_id, '提现成功', '提现金额：'+amount+'元')
        mes2bil(user_id, '提现', '-'+amount)
    return jsonify({'status': 'ok', 'message': newValue})


@app.route('/hourlycheck', methods=['POST'])
def hourlycheck():
    c = get_db().cursor()
    c.execute("SELECT * FROM deal_info")
    rows = c.fetchall()
    for row in rows:
        status = ''
        if row[3] == 'up2vip':
            now = datetime.datetime.now()
            year = now.year
            month = now.month
            day = now.day
            year += int(month/12)
            month = month%12+1
            des_time = datetime.date(year, month, day)
            status = ast.literal_eval(up2vip(row[1], des_time.year, des_time.month, des_time.day, row[6], False).get_data().decode("utf-8"))
        elif row[3] == 'extendvip':
            status = ast.literal_eval(extendvip(row[1], row[5], row[6], False).get_data().decode("utf-8"))
        else:
            status = ast.literal_eval(extendagent(row[1], row[3], row[4], row[5], row[6], False).get_data().decode("utf-8"))
        if status['status'] == 'ok':
            c.execute("DELETE FROM deal_info WHERE deal_id = ?",(row[0],))
            get_db().commit()
        else:
            now = datetime.datetime.now()
            if int(ret[7]) >= now.year:
                if int(ret[8]) >= now.month:
                    if int(ret[9]) >= now.day:
                        if int(ret[10]) >= now.hour:
                            pass
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
            api_uplevel(row[1])
            print(status, file=sys.stderr)
    return jsonify({'status': 'Hourly Checked'})


if __name__ == '__main__':
    #context = ('sslcrts/2_user.hanjianqiao.cn.crt', 'sslcrts/3_user.hanjianqiao.cn.key')
    #app.run(host='0.0.0.0', port=10010, ssl_context=context)
    app.run(port=10010)
