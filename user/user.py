# -*- coding: utf-8 -*- 

import os
from flask import Flask, url_for, redirect, render_template, request, abort
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
now = datetime.datetime.now()
thisMonthTableName = 'record_' + str(now.year) + '_' + str(now.month)


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


class DealInfo(db.Model):
    __tablename__ = thisMonthTableName
    deal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Text)
    inviter_id = db.Column(db.Text)
    type = db.Column(db.Text)
    need_invite = db.Column(db.Text)
    need_extend = db.Column(db.Text)
    fee = db.Column(db.Text)
    end_year = db.Column(db.Text)
    end_month = db.Column(db.Text)
    end_day = db.Column(db.Text)
    end_hour = db.Column(db.Text)
    end_minute = db.Column(db.Text)
    interval = db.Column(db.Text)


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text)
    inviter = db.Column(db.Text)
    code = db.Column(db.Text)
    email = db.Column(db.Text)
    qq = db.Column(db.Text)
    wechat = db.Column(db.Text)
    taobao = db.Column(db.Text)
    type = db.Column(db.Text)
    level = db.Column(db.Text)
    expire_year = db.Column(db.Text)
    expire_month = db.Column(db.Text)
    expire_day = db.Column(db.Text)
    balance = db.Column(db.Text)
    invitation_remain = db.Column(db.Text)
    extend_remain = db.Column(db.Text)
    invitee_total = db.Column(db.Text)
    invitee_vip = db.Column(db.Text)
    invitee_agent = db.Column(db.Text)
    team_total = db.Column(db.Text)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):
    # Visible columns in the list view
    #column_exclude_list = ['team_total']
    list_columns = ['deal_id', 'user_id', 'need_invite', 'need_extend', 'fee']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    column_sortable_list = ()

    # Rename 'title' columns to 'Post Title' in list view
    column_labels = dict(   deal_id=u'处理ID', user_id=u'用户名', inviter_id=u'上级', type=u'事件类型', need_invite=u'本月新增会员', need_extend=u'本月会员续费', fee=u'本月新增代理',
                            end_year=u'截止年份', end_month=u'截止月份', end_day=u'截止日', end_hour=u'截止小时', end_minute=u'截止分钟', interval=u'等待时间')

    column_searchable_list = ('inviter_id',)

    column_filters = ('user_id',)

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
    list_columns = ['user_id', 'inviter', 'code', 'qq', 'wechat', 'expire_year', 'expire_month', 'expire_day', 'type', 'level', 'balance', 'invitation_remain', 'extend_remain', 'invitee_total', 'invitee_vip', 'invitee_agent']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    column_sortable_list = ()

    # Rename 'title' columns to 'Post Title' in list view
    column_labels = dict(user_id=u'用户名', inviter=u'上级', code=u'邀请码', email=u'邮件', qq=u'QQ', wechat=u'微信', taobao=u'淘宝账号', type=u'类型', level=u'级别', expire_year=u'到期年份', expire_month=u'到期月份', expire_day=u'到期日', balance=u'余额', invitation_remain=u'剩余邀请', extend_remain=u'剩余续费', invitee_total=u'总邀请人数', invitee_vip=u'邀请VIP数', invitee_agent=u'邀请代理数')

    column_searchable_list = ('user_id',)

    column_filters = ('inviter', 'wechat', 'code', 'expire_month', 'expire_day', 'balance', 
                      filters.FilterLike(UserInfo.type, u'类型', options=(('user', u'普通用户'), ('vip', u'VIP及代理'))),
                      filters.FilterLike(UserInfo.level, u'级别',
                            options=(('user', u'普通用户'), ('vip', u'会员'), ('agent', u'永久代理'), ('golden', u'永久金牌代理'), ('agent_lt', u'代理'), ('golden_lt', u'金牌代理'), ('cofound', u'联合创始人'))))

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

# Create admin
admin = flask_admin.Admin(
    app,
    u'小牛快淘用户后台管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)


# Add model views
#admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(DealInfo, db.session))
admin.add_view(MyModelView2(UserInfo, db.session))


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


def add_admin_user():
    """
    Populate a small db with some example entries.
    """
    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='poiuy',
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
    #if os.path.exists(database_path):
    #    build_sample_db()
    if not User.query.filter_by(first_name='poiuy').first():
        add_admin_user()
    # Start app
    context = ('/home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.pem',
        '/home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.key')
    app.run(host='0.0.0.0', port=7009, ssl_context=context, debug=True)
    #app.run(host='0.0.0.0', port=7009, debug=True)
