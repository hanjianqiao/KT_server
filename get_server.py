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
        return jsonify({'status': 'ok', 'message': 'login ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/query', methods=['POST'])
def api_query():
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
        inviter, code, email, qq, wechat, taobao, type, level, expire_year, expire_month,
        expire_day, balance, invitation_remain, extend_remain, invitee_total, invitee_vip,
        invitee_agent, team_total = ret[0][2:]

        data = {'user_id': user_id, 'inviter': inviter, 'code': code,
                'email': email, 'qq': qq, 'wechat': wechat, 'taobao': taobao, 'type': type,
                'level': level, 'expire_year': expire_year, 'expire_month': expire_month,
                'expire_day': expire_day, 'balance': balance, 'invitation_remain': invitation_remain,
                'extend_remain': extend_remain, 'invitee_total': invitee_total, 'invitee_vip': invitee_vip,
                'invitee_agent': invitee_agent, 'team_total': team_total}
        return jsonify({'status': 'ok', 'message': 'login ok', 'data': data})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


# Mall Pages
@app.route('/recommend', methods=['GET'])
def page_recommend():
    filename = os.path.join(current_path, 'recommend.html')
    with codecs.open(filename, 'r', 'utf-8') as f:
        return f.read()


@app.route('/selfchoose', methods=['GET'])
def page_self_choose():
    filename = os.path.join(current_path, 'selfchoose.html')
    with codecs.open(filename, 'r', 'utf-8') as f:
        return f.read()


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=443, ssl_context=context)
