from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='/A', static_folder='../html/static/simple/')

if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=20000, ssl_context=context)
    #app.run(host='0.0.0.0', port=20000)