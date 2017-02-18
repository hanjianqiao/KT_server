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
database_path = os.path.join(database_folder, 'message.db')


def get_db():
    db = getattr(g, '_mesdatabase', None)
    if db is None:
        db = g._mesdatabase = sqlite3.connect(database_path)

        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = c.fetchall()
        if not table_list:
            c.execute("""
                CREATE TABLE user_info (message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id TEXT,
                                        title TEXT,
                                        date TEXT,
                                        body TEXT)
                """)
            c.execute("""
                CREATE TABLE user_status (  user_id TEXT,
                                            isThere TEXT)
                """)
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_mesdatabase', None)
    if db is not None:
        db.close()


@app.route('/add', methods=['POST'])
def add():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        userid = info_data.get('userid', '')
        title = info_data.get('title', '')
        body = info_data.get('body', '')
        c = get_db().cursor()
        now = datetime.datetime.now()
        c.execute("INSERT INTO user_info (user_id, title, date, body) VALUES (?, ?, ?, ?)",
                      (userid, title, now.strftime("%Y-%m-%d %H:%M"), body,))

        c.execute("SELECT * FROM user_status WHERE user_id = ?", (userid,))
        users = c.fetchall()
        if len(users) == 0:
            c.execute("INSERT INTO user_status (user_id, isThere) VALUES (?, ?)", (userid, 'yes'))
        else:
            c.execute("UPDATE user_status SET isThere = ? where user_id = ?", ('yes',userid,))
        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/list', methods=['GET'])
def api_list():
    id = request.args.get('userid')
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info where user_id = ?", (id,))
    rows = c.fetchall()
    ret = []
    for row in rows:
        ret.append({'title': row[2], 'id': row[0]})

    c.execute("UPDATE user_status SET isThere = ? where user_id = ?", ('no',id,))
    get_db().commit()

    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/check', methods=['POST'])
def api_check():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        userid = info_data.get('user_id', '')
        c = get_db().cursor()
        c.execute("SELECT * FROM user_status WHERE user_id = ?", (userid,))
        row = c.fetchone()
        return jsonify({'status': 'ok',
                        'message': row[1]
                    })
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/detail', methods=['GET'])
def api_detail():
    id = request.args.get('id')
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info WHERE message_id = ?", (id,))
    row = c.fetchone()
    # c.execute("DELETE FROM user_info WHERE message_id = ?", (id,))
    get_db().commit()
    return jsonify({'status': 'ok',
                    'message':{
                        'title': row[2],
                        'date': row[3],
                        'body': row[4]
                    }
                })


if __name__ == '__main__':
    context = ('sslcrts/2_user.hanjianqiao.cn.crt', 'sslcrts/3_user.hanjianqiao.cn.key')
    app.run(host='0.0.0.0', port=30000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
