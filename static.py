from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='/A', static_folder='../html/static/simple/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

