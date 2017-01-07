import os
import re
import random
import codecs
import hashlib
import sqlite3
from flask import *

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
        inviter_row = c.fetchone()
        if not inviter_row:
            return jsonify({'status': 'failed', 'message': 'code not exist'})
        inviter = inviter_row[0]

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
                  (user_id, secret, inviter, '000000', email, qq, wechat, taobao, 'user',
                   'user', '2017', '01', '01', '0', '0', '0', '0', '0', '0', '0'))
        c.execute("SELECT invitee_total FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchone()
        invitee_total = inviter_row[0]
        newValue = str(int(invitee_total)+1)
        c.execute("UPDATE user_info SET invitee_total = ? WHERE user_id = ?",(newValue, inviter,))

        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'register ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/up2vip', methods=['POST'])
def api_up2vip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        expire_year = info_data.get('expire_year', '')
        expire_month = info_data.get('expire_month', '')
        expire_day = info_data.get('expire_day', '')

        c = get_db().cursor()

        # check inviter's remains
        c.execute("SELECT inviter FROM user_info WHERE userid = ?", (user_id,))
        inviter_row = c.fetchone()
        inviter = inviter_row[0]
        c.execute("SELECT invitee_vip, invitation_remain FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchone()
        invitee_vip = inviter_row[0][0]
        invitation_remain = inviter_row[0][1]
        if int(invitation_remain) < 1:
            return 'remains'
        invitee_vip = str(int(invitee_vip)+1)
        invitation_remain = str(int(invitation_remain)-1)

        # update user's infomation
        c.execute("SELECT expire_year FROM user_info WHERE user_id = 13900000000")
        inviter_row = c.fetchone()
        code = inviter_row[0]
        newValue = str(int(code)+1)
        c.execute("UPDATE user_info SET expire_year = ? WHERE user_id = 13900000000",(newValue,))
        c.execute("UPDATE user_info SET expire_year = ?, expire_month = ?, expire_day = ?, code = ?, type = ?, level = ? WHERE user_id = ?",
                                      (expire_year, expire_month, expire_day, code, 'vip', 'vip', user_id,))

        # update inviter's information
        c.execute("UPDATE user_info SET invitee_vip = ?, invitation_remain = ? WHERE user_id = ?",(invitee_vip, invitation_remain, inviter,))

        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'upgrade ok'})
    return jsonify({'status': 'failed'})


@app.route('/extendvip', methods=['POST'])
def api_extendvip():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        extend_month = info_data.get('extend_month', '')

        c = get_db().cursor()

        # check inviter's remains
        c.execute("SELECT inviter FROM user_info WHERE userid = ?", (user_id,))
        inviter_row = c.fetchone()
        inviter = inviter_row[0]
        c.execute("SELECT extend_remain FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchone()
        extend_remain = inviter_row[0]
        if int(extend_remain) < int(extend_month):
            return 'remains'
        extend_remain = str(int(extend_remain)-int(extend_month))

        # update user's infomation
        c.execute("SELECT expire_year, expire_month FROM user_info WHERE user_id= ?", (user_id,))
        ret = c.fetchall()
        expire_year = str(int(ret[0][0])+(int(ret[0][1])-1+int(extend_month))/12)
        expire_month = str((int(ret[0][1])-1+int(extend_month))%12+1)
        c.execute("UPDATE user_info SET expire_year = ?, expire_month = ? WHERE user_id = ?",
                                      (expire_year, expire_month, user_id,))

        # update inviter's information
        c.execute("UPDATE user_info SET extend_remain = ? WHERE user_id = ?",(extend_remain, inviter,))

        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'upgrade ok'})
    return jsonify({'status': 'failed'})


@app.route('/extendagent', methods=['POST'])
def api_extendagent():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        level = info_data.get('level', '')
        invitation = info_data.get('invitation', '')
        extend = info_data.get('extend', '')

        c = get_db().cursor()
        # check inviter's remains
        c.execute("SELECT inviter FROM user_info WHERE userid = ?", (user_id,))
        inviter_row = c.fetchone()
        inviter = inviter_row[0]
        c.execute("SELECT invitee_agent, invitation_remain, extend_remain FROM user_info WHERE user_id = ?",(inviter,))
        inviter_row = c.fetchone()
        invitation_remain = inviter_row[0][0]
        extend_remain = inviter_row[0][1]
        invitee_agent = inviter_row[0][2]
        if int(invitation_remain) < int(invitation):
            return 'remains'
        if int(extend_remain) < int(extend):
            return 'remains'
        invitation_remain = str(int(invitation_remain)-int(invitation))
        extend_remain = str(int(extend_remain)-int(extend))

        # update user's infomation
        c.execute("SELECT invitation_remain, extend_remain, level FROM user_info WHERE user_id = ?",(user_id,))
        inviter_row = c.fetchone()
        user_invitation_remain = str(int(inviter_row[0][0])+int(invitation))
        user_extend_remain = str(int(inviter_row[0][1])+int(extend))
        user_level = inviter_row[0][2]
        if user_level == 'vip':
            invitee_agent = str(int(invitee_agent)+1)
        c.execute("UPDATE user_info SET invitation_remain = ?, extend_remain = ? WHERE user_id = ?",
                  (user_invitation_remain, user_extend_remain, user_id,))

        # update inviter's information
        c.execute("UPDATE user_info SET invitee_agent = ?, invitation_remain = ?, extend_remain = ? WHERE user_id = ?",
                  (invitee_agent, invitation_remain, extend_remain, inviter,))

        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'upgrade ok'})
    return jsonify({'status': 'failed'})


if __name__ == '__main__':
    #context = ('server.crt', 'server.key')
    #app.run(host='0.0.0.0', port=2000, ssl_context=context)
    app.run(host='0.0.0.0', port=2000)
