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
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_mesdatabase', None)
    if db is not None:
        db.close()


@app.route('/add', methods=['POST'])
def add():
    c = get_db().cursor()
    now = datetime.datetime.now()
    c.execute("INSERT INTO user_info (user_id, title, date, body) VALUES (?, ?, ?, ?)",
                  ('0', '问候', now.strftime("%Y-%m-%d %H:%M"), now.strftime("你好！\n%H点%M分快乐！"),))
    get_db().commit()
    return jsonify({'status': 'ok', 'message': 'ok'})


@app.route('/list', methods=['GET'])
def api_list():
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info")
    rows = c.fetchall()
    ret = []
    for row in rows:
        ret.append({'title': row[2]+str(row[0]), 'id': row[0]})

    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/check', methods=['POST'])
def api_check():
    c = get_db().cursor()
    c.execute("SELECT * FROM sqlite_sequence")
    row = c.fetchone()
    return jsonify({'status': 'ok',
                    'message': row[1]
                })


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
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=30000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
