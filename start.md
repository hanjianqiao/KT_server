requirements-dev:

Flask>=0.7
Flask-SQLAlchemy>=0.15
peewee
wtf-peewee
mongoengine<0.11.0
pymongo==2.8
flask-mongoengine==0.8.2
pillow==2.9.0
Babel<=1.3
flask-babelex
shapely==1.5.9
geoalchemy2
psycopg2
nose
sphinx
sphinx-intl
coveralls
pylint



nohup python3 set_server.py 2>set.log &

nohup python3 get_server.py 2>get.log &

nohup python3 bill/app.py 2>bil.log &

nohup python3 message/app.py 2>mes.log &

nohup python3 good/app.py 2>goo.log &

nohup python3 recommend/app.py 2>rec.log &

nohup python3 periodic.py 2>per.log &

nohup python3 charger/app.py 2>cha.log &

nohup python user/app.py 2>use.log &