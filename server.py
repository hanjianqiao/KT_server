import os
import sqlite3
from flask import *
app = Flask(__name__)

current_path = os.path.dirname(__file__)
database_folder = os.path.join(current_path, 'database')
if not os.path.exists(database_folder):
    os.mkdir(database_folder)
database_path = os.path.join(database_folder, 'user_info.db')

conn = sqlite3.connect(database_path)
c = conn.cursor()
# noinspection SqlResolve
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_list = c.fetchall()

if not table_list:
    c.execute("CREATE TABLE user_info (user_id TEXT, password TEXT, code TEXT, qq TEXT, wechat TEXT, taobao TEXT)")
    conn.commit()


@app.route('/register', methods=['POST'])
def api_register():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        user_id = info_data.get('user_id', '')
        password = info_data.get('password', '')
        code = info_data.get('code', '')
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

        # user_id exists check
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id, ))
        if c.fetchall():
            return jsonify({'status': 'failed', 'message': 'user_id already exists'})

        c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?)", (user_id, password, code, qq, wechat, taobao))
        conn.commit()
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
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id, ))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if ret[0][1] != password:
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
        c.execute("SELECT * FROM user_info WHERE user_id=?", (user_id, ))
        ret = c.fetchall()
        if not ret:
            return jsonify({'status': 'failed', 'message': 'user_id not exists'})
        if ret[0][1] != password:
            return jsonify({'status': 'failed', 'message': 'password not match'})
        code, qq, wechat, taobao = ret[0][2:]

        data = {'user_id': user_id, 'code': code, 'qq': qq, 'wechat': wechat, 'taobao': taobao}
        return jsonify({'status': 'ok', 'message': 'login ok', 'data': data})
    return jsonify({'status': 'failed', 'message': 'json data format error'})

app.run(host='0.0.0.0')
