from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='/A', static_folder='../html/static/simple/')

if __name__ == '__main__':
    context = ('sslcrts/2_shop.hanjianqiao.cn.crt', 'sslcrts/3_shop.hanjianqiao.cn.key')
    app.run(host='0.0.0.0', port=7741, ssl_context=context)
    #app.run(host='0.0.0.0', port=20000)