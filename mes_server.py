import json
import ssl
from flask import *

app = Flask(__name__)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/list', methods=['GET'])
def api_list():
    return jsonify({'status': 'ok',
                    'message':[
                        {'title': '消息概述', 'id': "11"},
                        {'title': '消息概述', 'id': "11"},
                        {'title': '消息概述', 'id': "11"},
                        {'title': '消息概述', 'id': "11"},
                        {'title': '消息概述', 'id': "11"},
                        {'title': '消息概述', 'id': "11"}
                    ]
                })


@app.route('/detail', methods=['GET'])
def api_detail():
    return jsonify({'status': 'ok',
                    'message':{
                        'title': '这是信息题目',
                        'date': '这是信息时间',
                        'body': '这是信息内容'
                    }
                })


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=30000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
