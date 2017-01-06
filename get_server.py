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
                                        taobao TEXT)
                """)
            c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      ('13800000000', '', '13800000000', '666666',
                       'admin@kouchenvip.com', '', '', ''))
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


def random_code():
    c = get_db().cursor()
    for i in range(10):
        code = '{:06d}'.format(random.randrange(0, 1000000))
        c.execute("SELECT code FROM user_info WHERE code=?", (code,))
        if not c.fetchone():
            return code
    return '666666'


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
        c.execute("SELECT user_id FROM user_info WHERE code=?", (code,))
        inviter_row = c.fetchone()
        if not inviter_row:
            return jsonify({'status': 'failed', 'message': 'code not exist'})
        inviter = inviter_row[0]
        code = random_code()

        # user_id exists check
        c.execute("SELECT user_id FROM user_info WHERE user_id=?", (user_id,))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': 'user_id already exists'})

        # email exists check
        c.execute("SELECT email FROM user_info WHERE email=?", (email,))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': 'email already exists'})

        secret = secret_pass(password)
        c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_id, secret, inviter, code, email, qq, wechat, taobao))
        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'register ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


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
        inviter, code, email, qq, wechat, taobao = ret[0][2:]

        data = {'user_id': user_id, 'inviter': inviter, 'code': code,
                'email': email, 'qq': qq, 'wechat': wechat, 'taobao': taobao}
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


@app.route('/inc', methods=['POST'])
def inc():
    c = get_db().cursor()
    c.execute("SELECT inviter FROM user_info WHERE user_id = 13800000000")
    inviter_row = c.fetchone()
    inviter = inviter_row[0]
    newValue = str(int(inviter)+1)
    c.execute("UPDATE user_info SET inviter = ? WHERE user_id = 13800000000",(newValue,))
    get_db().commit()
    return jsonify({'status': newValue})


@app.route('/dec', methods=['POST'])
def dec():
    c = get_db().cursor()
    c.execute("SELECT inviter FROM user_info WHERE user_id = 13800000000")
    inviter_row = c.fetchone()
    inviter = inviter_row[0]
    newValue = str(int(inviter)-1)
    c.execute("UPDATE user_info SET inviter = ? WHERE user_id = 13800000000",(newValue,))
    get_db().commit()
    return jsonify({'status': newValue})


if __name__ == '__main__':
    #context = ('server.crt', 'server.key')
    #app.run(host='0.0.0.0', port=5000, ssl_context=context)
    app.run(host='0.0.0.0', port=5000)
