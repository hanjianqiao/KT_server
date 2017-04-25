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

deltaHours = 20
deltaMinutes = 10

# headers
headers = {'Content-type': 'application/json'}

def mes2user(userid, title, body):
    # charge user
    # create a unverified https connection to set server
    #context = ssl._create_unverified_context()
    connection = http.client.HTTPConnection('user.hanjianqiao.cn', 30000)
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
    #context = ssl._create_unverified_context()
    connection = http.client.HTTPConnection('user.hanjianqiao.cn', 40000)
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
            return jsonify({'status': 'failed', 'message': '用户名格式错误，请使用手机号码'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': '密码格式错误，请使用6位以上密码'})
        if not (isinstance(code, str) and len(code) == 6 and all(map(lambda d: d.isdigit(), code))):
            return jsonify({'status': 'failed', 'message': '邀请码格式错误'})
        if code == '000000':
            return jsonify({'status': 'failed', 'message': '邀请码错误'})
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
    c.execute("SELECT expire_year, expire_month, expire_day FROM user_info WHERE user_id= ?", (inviter,))
    ret = c.fetchall()
    now = datetime.datetime.now()
    isExpired = False
    if int(ret[0][0]) < now.year:
        isExpired = True
    elif int(ret[0][0]) == now.year:
        if int(ret[0][1]) < now.month:
            isExpired = True
        elif int(ret[0][1]) == now.month:
            if int(ret[0][2]) < now.day:
                isExpired = True
    if isExpired == True:
        return jsonify({'status': 'failed', 'message': '您的邀请者'+inviter+'目前不是会员，无法邀请您加入'})
    if user_level != 'user':
        return jsonify({'status': 'failed', 'message': '你已经是VIP'})
    if int(user_balance) < int(fee):
        return jsonify({'status': 'failed', 'message': '帐户余额不足，请点击头像进入财富中心充值'})
    c.execute("SELECT invitee_vip, invitation_remain, balance FROM user_info WHERE user_id = ?",(inviter,))
    inviter_row = c.fetchall()
    invitee_vip = inviter_row[0][0]
    invitation_remain = inviter_row[0][1]
    inviter_balance = inviter_row[0][2]

    if int(invitation_remain) < 1:
        searchTarget = inviter
        while True:
            c.execute("SELECT inviter, invitation_remain FROM user_info WHERE user_id = ?", (searchTarget,))
            ret = c.fetchall()
            if int(ret[0][1]) > 0:
                break;
            if searchTarget == '13800000000':
                break;
            searchTarget = ret[0][0]
        c.execute("SELECT invitation_remain FROM user_info WHERE user_id = ?", (searchTarget,))
        ret = c.fetchall()
        new_int_remain = str(int(ret[0][0])-1)
        c.execute("UPDATE user_info SET invitation_remain = ? WHERE user_id = ?",
              (new_int_remain, searchTarget,))
        mes2user(searchTarget, '邀请次数被使用', '用户'+user_id+'使用你的邀请次数升级VIP')
        mes2user(user_id, '使用代理邀请次数升级', '您使用'+searchTarget+'的邀请次数升级为VIP')
    else:
        invitation_remain = str(int(invitation_remain)-1)
        #inviter_balance = str(int(inviter_balance)+int(fee))
        mes2user(inviter, '邀请次数被使用', '用户'+user_id+'使用你的邀请次数升级VIP')
        mes2user(user_id, '使用代理邀请次数升级', '您使用'+inviter+'的邀请次数升级为VIP')
        #mes2bil(inviter, '售出邀请名额', '+'+fee)

    invitee_vip = str(int(invitee_vip)+1)
    user_balance = str(int(user_balance)-int(fee))

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

    # record number of vip
    c.execute("SELECT need_invite, need_extend, fee FROM deal_info WHERE user_id=?", (inviter,))
    ret = c.fetchall()
    if ret:
        need_invite = str(int(ret[0][0])+1)
        c.execute("UPDATE deal_info SET need_invite = ? WHERE user_id = ?",
              (need_invite, inviter,))
    else:
        c.execute("INSERT INTO deal_info (user_id, need_invite, need_extend, fee) VALUES (?, ?, ?, ?)",
                (inviter, '1', '0', '0'))

    get_db().commit()
    mes2user(user_id, '恭喜升级VIP', '欢迎加入VIP，现在请使用佣金及优惠券查询功能')
    mes2user(inviter, '下级升级VIP', '您的下级已升级为VIP：'+user_id)
    mes2bil(user_id, '购买VIP', '-'+fee)
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
    c.execute("SELECT inviter, balance, level, type FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    user_balance = inviter_row[0][1]
    user_level = inviter_row[0][2]
    user_type = inviter_row[0][3]
    c.execute("SELECT expire_year, expire_month, expire_day FROM user_info WHERE user_id= ?", (inviter,))
    ret = c.fetchall()
    now = datetime.datetime.now()
    isExpired = False
    if int(ret[0][0]) < now.year:
        isExpired = True
    elif int(ret[0][0]) == now.year:
        if int(ret[0][1]) < now.month:
            isExpired = True
        elif int(ret[0][1]) == now.month:
            if int(ret[0][2]) < now.day:
                isExpired = True
    if isExpired == True:
        return jsonify({'status': 'failed', 'message': '您的邀请者'+inviter+'目前不是会员，无法续费'})
    if user_type == 'user':
        return jsonify({'status': 'failed', 'message': '请先升级为VIP'})
    else:
        if int(user_balance) < int(fee):
            return jsonify({'status': 'failed', 'message': '帐户余额不足，请点击头像进入财富中心充值'})

        # update user's infomation
        user_balance = str(int(user_balance)-int(fee))
        c.execute("SELECT expire_year, expire_month, expire_day FROM user_info WHERE user_id= ?", (user_id,))
        ret = c.fetchall()
        now = datetime.datetime.now()
        isExpired = False
        if int(ret[0][0]) < now.year:
            isExpired = True
        elif int(ret[0][0]) == now.year:
            if int(ret[0][1]) < now.month:
                isExpired = True
            elif int(ret[0][1]) == now.month:
                if int(ret[0][2]) < now.day:
                    isExpired = True
        expire_year = ret[0][0]
        expire_month = ret[0][1]
        expire_day = ret[0][2]
        if isExpired == False:
            expire_year = str(int(int(ret[0][0])+(int(ret[0][1])-1+int(extend_month))/12))
            expire_month = str((int(ret[0][1])-1+int(extend_month))%12+1)
        else:
            expire_year = str(int(now.year+(now.month-1+int(extend_month))/12))
            expire_month = str((now.month-1+int(extend_month))%12+1)
            expire_day = now.day;
        c.execute("UPDATE user_info SET balance = ?, expire_year = ?, expire_month = ?, expire_day = ? WHERE user_id = ?",
                                      (user_balance, expire_year, expire_month, expire_day, user_id,))
        mes2bil(user_id, 'VIP延长'+extend_month+'个月', '-'+fee)
        mes2user(user_id, '成功延长VIP', '您的VIP延长了'+extend_month+'个月')

        # update inviter's information
        c.execute("SELECT balance FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchall()
        inviter_balance = str(int(inviter_row[0][0])+50*int(extend_month))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",
                  (inviter_balance, inviter,))
        mes2bil(inviter, '邀请用户VIP延长'+extend_month+'个月', '+'+str(50*int(extend_month)))
        mes2user(inviter, '用户延长VIP', '您邀请的用户'+user_id+'VIP延长'+extend_month+'个月')

        # update agent's information
        searchTarget = inviter
        while True:
            c.execute("SELECT expire_year, expire_month, expire_day, inviter, level FROM user_info WHERE user_id = ?", (searchTarget,))
            ret = c.fetchall()
            now = datetime.datetime.now()
            isExpired = False
            if int(ret[0][0]) < now.year:
                isExpired = True
            elif int(ret[0][0]) == now.year:
                if int(ret[0][1]) < now.month:
                    isExpired = True
                elif int(ret[0][1]) == now.month:
                    if int(ret[0][2]) < now.day:
                        isExpired = True
            if (isExpired == False) and (ret[0][4] == 'agent' or ret[0][4] == 'golden' or ret[0][4] == 'cofound'):
                break;
            if searchTarget == '13800000000':
                break;
            searchTarget = ret[0][3]
        c.execute("SELECT balance FROM user_info WHERE user_id = ?",(searchTarget,))
        inviter_row = c.fetchall()
        inviter_balance = str(int(inviter_row[0][0])+18*int(extend_month))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",
                  (inviter_balance, searchTarget,))
        mes2bil(searchTarget, '代理VIP延长收益：'+extend_month+'个月', '+'+str(18*int(extend_month)))
        mes2user(searchTarget, '代理：用户延长VIP', '用户'+user_id+'VIP延长'+extend_month+'个月')

        # update golden's information
        searchTarget = inviter
        while True:
            c.execute("SELECT expire_year, expire_month, expire_day, inviter, level FROM user_info WHERE user_id = ?", (searchTarget,))
            ret = c.fetchall()
            now = datetime.datetime.now()
            isExpired = False
            if int(ret[0][0]) < now.year:
                isExpired = True
            elif int(ret[0][0]) == now.year:
                if int(ret[0][1]) < now.month:
                    isExpired = True
                elif int(ret[0][1]) == now.month:
                    if int(ret[0][2]) < now.day:
                        isExpired = True
            if (isExpired == False) and (ret[0][4] == 'golden' or ret[0][4] == 'cofound'):
                break;
            if searchTarget == '13800000000':
                break;
            searchTarget = ret[0][3]
        c.execute("SELECT balance FROM user_info WHERE user_id = ?",(searchTarget,))
        inviter_row = c.fetchall()
        inviter_balance = str(int(inviter_row[0][0])+10*int(extend_month))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",
                  (inviter_balance, searchTarget,))
        mes2bil(searchTarget, '金牌VIP延长收益：'+extend_month+'个月', '+'+str(10*int(extend_month)))
        mes2user(searchTarget, '金牌：用户延长VIP', '用户'+user_id+'VIP延长'+extend_month+'个月')

        # update cofound's information
        searchTarget = inviter
        while True:
            c.execute("SELECT expire_year, expire_month, expire_day, inviter, level FROM user_info WHERE user_id = ?", (searchTarget,))
            ret = c.fetchall()
            now = datetime.datetime.now()
            isExpired = False
            if int(ret[0][0]) < now.year:
                isExpired = True
            elif int(ret[0][0]) == now.year:
                if int(ret[0][1]) < now.month:
                    isExpired = True
                elif int(ret[0][1]) == now.month:
                    if int(ret[0][2]) < now.day:
                        isExpired = True
            if (isExpired == False) and (ret[0][4] == 'cofound'):
                break;
            if searchTarget == '13800000000':
                break;
            searchTarget = ret[0][3]
        c.execute("SELECT balance FROM user_info WHERE user_id = ?",(searchTarget,))
        inviter_row = c.fetchall()
        inviter_balance = str(int(inviter_row[0][0])+10*int(extend_month))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",
                  (inviter_balance, searchTarget,))
        mes2bil(searchTarget, '联合VIP延长收益：'+extend_month+'个月', '+'+str(10*int(extend_month)))
        mes2user(searchTarget, '联合：用户延长VIP', '用户'+user_id+'VIP延长'+extend_month+'个月')

        # record number of vip
        c.execute("SELECT need_invite, need_extend, fee FROM deal_info WHERE user_id=?", (inviter,))
        ret = c.fetchall()
        if ret:
            need_extend = str(int(ret[0][0])+int(extend_month))
            c.execute("UPDATE deal_info SET need_extend = ? WHERE user_id = ?",
                  (need_extend, inviter,))
        else:
            c.execute("INSERT INTO deal_info (user_id, need_invite, need_extend, fee) VALUES (?, ?, ?, ?)",
                    (inviter, '0', extend_month, '0'))

        get_db().commit()
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
    return jsonify({'status': 'ok', 'message': user_id+'操作后金额：'+newValue})


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
    return jsonify({'status': 'ok', 'message': user_id+'操作后金额：'+newValue})


if __name__ == '__main__':
    #context = ('sslcrts/2_user.hanjianqiao.cn.crt', 'sslcrts/3_user.hanjianqiao.cn.key')
    #app.run(host='0.0.0.0', port=10010, ssl_context=context)
    app.run(port=10010, debug=True)
