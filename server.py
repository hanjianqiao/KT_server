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
        info_list = tuple(info_data.values())

        if len(info_list) == 6:
            c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?, ?)", info_list)
            resp = jsonify({'status': 'ok', 'message': 'register fine'})
            return resp
        else:
            resp = jsonify({'status': 'failed', 'message': 'register data format error'})
            return resp
    resp = jsonify({'status': 'failed', 'message': 'bad request'})
    return resp

app.run()
