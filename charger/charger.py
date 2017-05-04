# -*- coding: utf-8 -*- 
import os
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask.ext.admin.contrib.sqla import filters
import ssl
from flask_babelex import Babel
import http.client
import json
import datetime

import hashlib



# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class MoneyLog(db.Model):
    __tablename__ = 'money_log'
    actionid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Text)
    action = db.Column(db.Text)
    amount = db.Column(db.Text)
    newbalance = db.Column(db.Text)
    by = db.Column(db.Text)
    date = db.Column(db.Text)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Flask views
@app.route('/')
def home(message='kidding'):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('charge.html', data = message)
 

 # somewhere to login
@app.route("/md5", methods=["GET", "POST"])
def md5():
    if request.method == 'POST':
        username = request.form['origintext']      
        return Response('''
        <form action="" method="post">
            <p><input type=text name=origintext>
            <p><input type=submit value=生成>
        </form>
        ''' + hashlib.md5(username.encode('utf-8')).hexdigest())
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=origintext>
            <p><input type=submit value=生成>
        </form>
        ''')


@app.route('/add', methods=['POST'])
def do_charge():
    if not session.get('logged_in'):
        return render_template('login.html')
    userid = request.form['userid']
    action = request.form['action']
    amount = request.form['amount']
    if userid == '':
        return home('请输入用户名')
    # charge user
    # headers
    headers = {'Content-type': 'application/json'}
    connection = http.client.HTTPConnection('localhost', 10010)
    foo = { "user_id":userid,
            "amount":amount}
    json_foo = json.dumps(foo)
    if action == '0':
        if amount == '':
            return home('金额不能为空')
        connection.request('POST', '/charge', json_foo, headers)
    elif action == '1':
        if amount == '':
            return home('金额不能为空')
        connection.request('POST', '/drawback', json_foo, headers)
    else:
        connection.request('POST', '/sysup2vip', json_foo, headers)
    response = connection.getresponse()
    ret = (response.read().decode())
    connection.close()
    jo = json.loads(ret)
    if jo['status'] == 'ok' and action != '2':
        logitem = MoneyLog()
        logitem.userid = userid
        logitem.action = action
        logitem.amount = amount
        logitem.newbalance = jo['message']
        logitem.by = 'default admin'
        now = datetime.datetime.now()
        logitem.date = now.strftime("%Y-%m-%d %H:%M")
        db.session.add(logitem)
        db.session.commit()
    return home(jo['message'])


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return redirect('/')
    else:
        flash('wrong password!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/search', methods=['GET'])
def api_search():
    key = request.args.get('key')
    rows = GoodInfo.query.filter(GoodInfo.title.contains(key)).all()
    ret = []
    for row in rows:
        ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'comment': row.comment,
                    'price': row.price, 'url': row.url})
    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/query', methods=['GET'])
def api_query():
    id = request.args.get('id')
    rows = GoodInfo.query.filter_by(good_id=id).all()
    ret = []
    for row in rows:
        ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'comment': row.comment,
                    'price': row.price, 'url': row.url})
    return jsonify({'status': 'ok',
                    'message': ret
                })


# Create admin
admin = flask_admin.Admin(
    app,
    u'小牛快淘充值提现管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)


# Add model views
#admin.add_view(MyModelView(Role, db.session))
#admin.add_view(MyModelView(User, db.session))
#admin.add_view(MyModelView2(GoodInfo, db.session))


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    db.drop_all()
    db.create_all()
    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='goodhelper',
            email='xjk786@vsus.com',
            password=encrypt_password('xjskd839'),
            roles=[user_role, super_user_role]
        )

        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    #add_admin_user()
    # Start app
    #context = ('/home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.pem',
    #    '/home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.key')
    #app.run(host='0.0.0.0', port=2100, ssl_context=context, debug=True)
    app.run(host='0.0.0.0', port=2100, debug=True)
