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
import urllib



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


class GoodInfo(db.Model):
    __tablename__ = 'good_info'
    good_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    image = db.Column(db.Text)
    price = db.Column(db.Text)
    sell = db.Column(db.Text)
    url = db.Column(db.Text)


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
    list_columns = ['good_id', 'title', 'image', 'price', 'orprice', 'url']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    column_sortable_list = ()

    # Rename 'title' columns to 'Post Title' in list view
    column_labels = dict(good_id=u'商品编号', title=u'标题', image=u'图片', price=u'现价', sell=u'销量', url=u'淘宝链接')
    column_searchable_list = ('good_id',)

    column_filters = ('title',
                      filters.FilterLike(GoodInfo.title, u'标题', options=(('cloth', u'衣服'), ('pant', u'裤子'))))

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


@app.route('/search', methods=['GET'])
def api_search():
    key = request.args.get('key')
    rows = GoodInfo.query.filter(GoodInfo.title.contains(urllib.parse.unquote(key))).all()
    ret = []
    for row in rows:
        ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'sell': row.sell,
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
        ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'sell': row.sell,
                    'price': row.price, 'url': row.url})
    return jsonify({'status': 'ok',
                    'message': ret
                })


# Create admin
admin = flask_admin.Admin(
    app,
    u'小牛快淘自选商品后台管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)


# Add model views
#admin.add_view(MyModelView(Role, db.session))
#admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView2(GoodInfo, db.session))


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
            first_name='thisisadmin',
            email='thisisadmin',
            password=encrypt_password('helloadmin009'),
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
    context = ('/home/lct/user.server/sslcrts/2_shop.hanjianqiao.cn.crt', '/home/lct/user.server/sslcrts/3_shop.hanjianqiao.cn.key')
    #app.run(host='0.0.0.0', port=7009, ssl_context=context)
    app.run(host='0.0.0.0', port=7008, debug=True)
