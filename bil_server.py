import os
import re
import random
import codecs
import hashlib
import sqlite3
from flask import *
import datetime
import ast
import sys

app = Flask(__name__)

current_path = os.path.dirname(__file__)
database_folder = os.path.join(current_path, 'database')
if not os.path.exists(database_folder):
    os.mkdir(database_folder)
database_path = os.path.join(database_folder, 'bilog.db')


def get_db():
    db = getattr(g, '_bilogdatabase', None)
    if db is None:
        db = g._bilogdatabase = sqlite3.connect(database_path)

        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = c.fetchall()
        if not table_list:
            c.execute("""
                CREATE TABLE user_info (log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id TEXT,
                                        action TEXT,
                                        date TEXT,
                                        amount TEXT)
                """)
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_bilogdatabase', None)
    if db is not None:
        db.close()

@app.route('/add', methods=['POST'])
def api_add():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        userid = info_data.get('userid', '')
        action = info_data.get('action', '')
        amount = info_data.get('amount', '')
        c = get_db().cursor()
        now = datetime.datetime.now()
        c.execute("INSERT INTO user_info (user_id, action, date, amount) VALUES (?, ?, ?, ?)",
                      (userid, action, now.strftime("%Y-%m-%d %H:%M"), amount,))
        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/list', methods=['GET'])
def api_list():
    id = request.args.get('userid')
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info WHERE user_id = ?", (id,))
    rows = c.fetchall()
    ret = []
    for row in rows:
        log_id, userid, action, date, amount = row[0:]
        ret.append({'id': log_id, 'userid': userid, 'action': action, 'date': date, 'amount': amount})
    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/detail', methods=['GET'])
def api_detail():
    return jsonify({'status': 'ok',
                    'message':{
                        'title': '余额充值',
                        'value': '90.00',
                        'level': 'UD329328823',
                        'start': '2016-12-09 12:39:09',
                        'end': '2016-12-09 12:39:09',
                        'no': '12345134'
                    }
                })


if __name__ == '__main__':
    context = ('sslcrts/2_user.hanjianqiao.cn.crt', 'sslcrts/3_user.hanjianqiao.cn.key')
    app.run(host='0.0.0.0', port=40000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
