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
database_path = os.path.join(database_folder, 'good.db')


def get_db():
    db = getattr(g, '_goodatabase', None)
    if db is None:
        db = g._goodatabase = sqlite3.connect(database_path)

        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = c.fetchall()
        if not table_list:
            c.execute("""
                CREATE TABLE user_info (good_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        title TEXT,
                                        image TEXT,
                                        comment TEXT,
                                        price TEXT,
                                        url TEXT,
                                        modify TEXT)
                """)
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_goodatabase', None)
    if db is not None:
        db.close()

@app.route('/add', methods=['POST'])
def api_add():
    if request.headers['Content-Type'] == 'application/json':
        info_data = request.get_json(force=True, silent=True)
        title = info_data.get('title', '')
        image = info_data.get('image', '')
        comment = info_data.get('comment', '')
        price = info_data.get('price', '')
        url = info_data.get('url', '')
        c = get_db().cursor()
        now = datetime.datetime.now()
        c.execute("INSERT INTO user_info (title, image, comment, price, url, modify) VALUES (?, ?, ?, ?, ?, ?)",
                      (title, image, comment, price, url, now.strftime("%Y-%m-%d %H:%M"),))
        get_db().commit()
        return jsonify({'status': 'ok', 'message': 'ok'})
    return jsonify({'status': 'failed', 'message': 'json data format error'})


@app.route('/search', methods=['GET'])
def api_search():
    key = request.args.get('key')
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info WHERE comment LIKE ?", ("%"+str(key)+"%",))
    rows = c.fetchall()
    ret = []
    for row in rows:
        good_id, title, image, comment, price, url, modify = row[0:]
        ret.append({'good_id': good_id, 'title': title, 'image': image, 'comment': comment, 'price': price, 'url': url, 'modify': modify})
    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/query', methods=['GET'])
def api_query():
    id = request.args.get('id')
    c = get_db().cursor()
    c.execute("SELECT * FROM user_info WHERE good_id = ?", (id,))
    rows = c.fetchall()
    ret = []
    for row in rows:
        good_id, title, image, comment, price, url, modify = row[0:]
        ret.append({'good_id': good_id, 'title': title, 'image': image, 'comment': comment, 'price': price, 'url': url, 'modify': modify})
    return jsonify({'status': 'ok',
                    'message': ret
                })


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=30001, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
