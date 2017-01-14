import os
import re
import random
import codecs
import hashlib
import sqlite3
from flask import *
import datetime

app = Flask(__name__)

current_path = os.path.dirname(__file__)
database_folder = os.path.join(current_path, 'database')
if not os.path.exists(database_folder):
    os.mkdir(database_folder)
database_path = os.path.join(database_folder, 'user_info.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)

        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = c.fetchall()
        if not table_list:
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
        return "You're under the system, no upgrading"
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
            return jsonify({'status': 'failed', 'message': 'user_id format error'})
        if not (isinstance(password, str) and len(password) >= 6):
            return jsonify({'status': 'failed', 'message': 'password format error'})
        if not (isinstance(code, str) and len(code) == 6 and all(map(lambda d: d.isdigit(), code))):
            return jsonify({'status': 'failed', 'message': 'code format error'})
        if not (isinstance(email, str) and re.match(r'[^@]+@[^@]+\.[^@]+', email)):
            return jsonify({'status': 'failed', 'message': 'email format error'})

        c = get_db().cursor()

        # invitation code check
        c.execute("SELECT user_id FROM user_info WHERE code=?", (code,))
        inviter_row = c.fetchall()
        if not inviter_row:
            return jsonify({'status': 'failed', 'message': 'code not exist'})
        inviter = inviter_row[0][0]

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


def up2vip(user_id, expire_year, expire_month, expire_day, fee, log):
    c = get_db().cursor()

    # check inviter's remains
    c.execute("SELECT inviter, balance, level FROM user_info WHERE user_id = ?", (user_id,))
    inviter_row = c.fetchall()
    inviter = inviter_row[0][0]
    user_balance = inviter_row[0][1]
    user_level = inviter_row[0][2]
    if user_level != 'user':
        return jsonify({'status': 'failed', 'message': 'you are already a vip'})
    if int(user_balance) < int(fee):
        return jsonify({'status': 'failed', 'message': 'balance not enough'})
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
        return jsonify({'status': 'failed', 'message': str(inviter)+' remains:'+str(invitation_remain)+' need:'+str(1)})
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
    return jsonify({'status': 'ok', 'message': 'ok'})


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
        return jsonify({'status': 'failed', 'message': str(inviter)+' remains:'+str(extend_remain)+' need:'+str(extend_month)})
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
    return jsonify({'status': 'ok', 'message': 'ok'})


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
        return jsonify({'status': 'failed', 'message': "Please upgrade to be a VIP first"})
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
    return jsonify({'status': 'ok', 'message': 'ok'})

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

        c = get_db().cursor()
        c.execute("SELECT balance FROM user_info WHERE user_id = ?", (user_id,))
        inviter_row = c.fetchall()
        balance = inviter_row[0][0]
        newValue = str(int(balance)+int(amount))
        c.execute("UPDATE user_info SET balance = ? WHERE user_id = ?",(newValue, user_id,))
        get_db().commit()
    return jsonify({'status': 'ok', 'message': newValue})


@app.route('/hourlycheck', methods=['POST'])
def hourlycheck():
        c = get_db().cursor()
        c.execute("SELECT * FROM deal_info")
        rows = c.fetchall()
        for row in rows:
            if row[3] == 'up2vip':
                now = datetime.datetime.now()
                year = now.year
                month = now.month
                day = now.day
                year += int(month/12)
                month = month%12+1
                des_time = datetime.date(year, month, day)
                if up2vip(row[1], des_time.year, des_time.month, des_time.day, row[6], False) == 'sucess':
                    c.execute("DELETE FROM deal_info WHERE deal_id = ?",(row[0],))
                    get_db().commit()
            elif row[3] == 'extendvip':
                if extendvip(row[1], row[5], row[6], False) == 'sucess':
                    c.execute("DELETE FROM deal_info WHERE deal_id = ?",(row[0],))
                    get_db().commit()
            else:
                if extendagent(row[1], row[3], row[4], row[5], row[6], False) == 'sucess':
                    c.execute("DELETE FROM deal_info WHERE deal_id = ?",(row[0],))
                    get_db().commit()
        return jsonify({'status': 'Hourly Checked'})


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=10010, ssl_context=context)
    #app.run(host='0.0.0.0', port=2000)
