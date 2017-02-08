import json
import ssl
from flask import *

app = Flask(__name__)


@app.teardown_appcontext
def close_connection(exception):
    pass


@app.route('/list', methods=['GET'])
def api_list():
    return jsonify({'status': 'ok',
                    'message':[{
                        'action': '余额充值',
                        'date': '2016-12-09 12:39:09',
                        'amount': '90.00',
                        'status': '成功',
                        'id': '11'
                        },{
                        'action': '余额充值',
                        'date': '2016-12-09 12:39:09',
                        'amount': '90.00',
                        'status': '成功',
                        'id': '11'
                        },{
                        'action': '余额充值',
                        'date': '2016-12-09 12:39:09',
                        'amount': '90.00',
                        'status': '成功',
                        'id': '11'
                        },{
                        'action': '余额充值',
                        'date': '2016-12-09 12:39:09',
                        'amount': '90.00',
                        'status': '成功',
                        'id': '11'
                        }
                    ]
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
    context = ('2_user.hanjianqiao.cn.crt', '3_user.hanjianqiao.cn.key')
    app.run(host='0.0.0.0', port=40000, ssl_context=context)
    #app.run(host='0.0.0.0', port=3000)
