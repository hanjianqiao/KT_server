# -*- coding: utf-8 -*- 

import os
#from flask import Flask, url_for, redirect, render_template, request, abort
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
import datetime



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
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class AppStatus(db.Model):
    __tablename__ = 'app'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)


class iOSStatus(db.Model):
    __tablename__ = 'ios'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)


class AndroidStatus(db.Model):
    __tablename__ = 'android'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)


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


class MyModelView2(sqla.ModelView):
    # Visible columns in the list view
    #column_exclude_list = ['team_total']
    list_columns = ['log_id', 'key', 'value']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    #column_sortable_list = ()

    # Rename 'title' columns to 'Post Title' in list view
    column_labels = dict(log_id=u'记录编号', key=u'记录名称', value=u'记录值')
    #column_searchable_list = ('log_id',)

    #column_filters = ('action',)

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
def index():
    return render_template('index.html')


@app.route('/check', methods=['GET'])
def api_check():
    row_min = AppStatus.query.filter_by(key='min').first()
    row_cur = AppStatus.query.filter_by(key='current').first()
    min_version = '0'
    cur_version = '0'
    if row_min:
        min_version = row_min.value
    if row_cur:
        cur_version = row_cur.value
    db.session.commit()
    return jsonify({'status': 'ok',
                    'message': cur_version,
                    'min': min_version
                })

@app.route('/ios', methods=['GET'])
def api_ios():
    row_min = iOSStatus.query.filter_by(key='min').first()
    row_cur = iOSStatus.query.filter_by(key='current').first()
    min_version = '0'
    cur_version = '0'
    if row_min:
        min_version = row_min.value
    if row_cur:
        cur_version = row_cur.value
    db.session.commit()
    return jsonify({'status': 'ok',
                    'message': cur_version,
                    'min': min_version
                })

@app.route('/android', methods=['GET'])
def api_android():
    row_min = AndroidStatus.query.filter_by(key='min').first()
    row_cur = AndroidStatus.query.filter_by(key='current').first()
    min_version = '0'
    cur_version = '0'
    if row_min:
        min_version = row_min.value
    if row_cur:
        cur_version = row_cur.value
    db.session.commit()
    return jsonify({'status': 'ok',
                    'message': cur_version,
                    'min': min_version
                })


@app.route('/init', methods=['GET'])
def api_init():
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

# Create admin
admin = flask_admin.Admin(
    app,
    u'小牛快淘软件后台管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)


# Add model views
#admin.add_view(MyModelView(Role, db.session))
#admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView2(AppStatus, db.session))
admin.add_view(MyModelView2(iOSStatus, db.session))
admin.add_view(MyModelView2(AndroidStatus, db.session))


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
            first_name='admin',
            email='thisisadmin',
            password=encrypt_password('xh3jianke1'),
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
    #context = ('/home/lct/user.server/sslcrts/2_user.hanjianqiao.cn.crt', '/home/lct/user.server/sslcrts/3_user.hanjianqiao.cn.key')
    #app.run(host='0.0.0.0', port=40000, ssl_context=context)
    app.run(host='0.0.0.0', port=13420, debug=True)
