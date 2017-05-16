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
from xlrd import open_workbook
import xlrd
from decimal import Decimal
import datetime
import flask_excel as excel



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
    catalog = db.Column(db.Text)
    activity = db.Column(db.Text)
    off = db.Column(db.Text)
    rate = db.Column(db.Text)
    image = db.Column(db.Text)
    price = db.Column(db.Text)
    sell = db.Column(db.Text)
    url = db.Column(db.Text)
    expire = db.Column(db.Text)
    tb_token = db.Column(db.Text)


class OffGoodInfo(db.Model):
    __tablename__ = 'off_good_info'
    good_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    catalog = db.Column(db.Text)
    activity = db.Column(db.Text)
    off = db.Column(db.Text)
    rate = db.Column(db.Text)
    image = db.Column(db.Text)
    price = db.Column(db.Text)
    sell = db.Column(db.Text)
    url = db.Column(db.Text)
    expire = db.Column(db.Text)
    tb_token = db.Column(db.Text)


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
    list_columns = ['good_id', 'title', 'catalog', 'activity', 'off', 'rate', 'url', 'price', 'sell', 'expire']
    # List of columns that can be sorted. For 'user' column, use User.username as
    # a column.
    column_sortable_list = ('title', 'url', 'price', 'expire')

    # Rename 'title' columns to 'Post Title' in list view
    column_labels = dict(good_id=u'商品编号', catalog=u'分类', activity=u'活动', off=u'优惠券', rate=u'佣金比例', title=u'标题', image=u'图片', price=u'价格', sell=u'销量', url=u'淘宝链接', expire=u'下架时间', tb_token=u'淘口令')
    
    column_searchable_list = ('url',)

    column_filters = ('title', 'url', 'catalog', 'good_id', 'activity')

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


@app.route('/upload')
def upload_page():
    if not current_user.is_active or not current_user.is_authenticated:
        return redirect(url_for('security.login', next='/'))

    if current_user.has_role('superuser'):
         return render_template('upload.html')

    return redirect(url_for('security.login', next='/'))


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if not current_user.is_active or not current_user.is_authenticated:
        return redirect(url_for('security.login', next='/'))
    if current_user.has_role('superuser'):
        if request.method == 'POST':
            print(u'你好')
            file = request.files['file']
            if file.filename == '':
                return u'未选择文件'
            else:
                file.save('/home/lct/logs/tmp9s0d9.xls')
                wb = open_workbook('/home/lct/logs/tmp9s0d9.xls')
                for sheet in wb.sheets():
                    number_of_rows = sheet.nrows
                    number_of_columns = sheet.ncols

                    items = []

                    rows = []
                    for row in range(1, number_of_rows):
                        catalog = sheet.cell(row,1).value
                        if(catalog==''):
                            catalog = int(0)
                        else:
                            catalog = int(catalog)
                        activity = sheet.cell(row,2).value
                        if(activity==''):
                            activity = int(0)
                        else:
                            activity = int(activity)
                        originItem = GoodInfo.query.filter_by(url=sheet.cell(row,6).value).first()
                        expire_str = ''
                        #print("####row is %s" % sheet.cell(row,9).value)
                        if type(sheet.cell(row,9).value) is str:
                            excel_date = datetime.datetime.strptime(sheet.cell(row,9).value, '%Y-%m-%d %H:%M:%S')
                            expire_str = ''+str(excel_date.year)+'/'+str(excel_date.month)+'/'+str(excel_date.day)
                        else:
                            excel_date = xlrd.xldate_as_tuple(sheet.cell(row,9).value, 0)
                            expire_str = ''+str(excel_date[0])+'/'+str(excel_date[1])+'/'+str(excel_date[2])
                        if originItem == None:
                            item = GoodInfo(title=sheet.cell(row,0).value, catalog=catalog, activity=activity,
                                off=sheet.cell(row,3).value, rate=sheet.cell(row,4).value, image=sheet.cell(row,5).value,
                                url=sheet.cell(row,6).value, price=sheet.cell(row,7).value, sell=sheet.cell(row,8).value,
                                expire=expire_str, tb_token='')
                            db.session.add(item)
                        else:
                            db.session.delete(originItem)
                            item = GoodInfo(title=sheet.cell(row,0).value, catalog=catalog, activity=activity,
                                off=sheet.cell(row,3).value, rate=sheet.cell(row,4).value, image=sheet.cell(row,5).value,
                                url=sheet.cell(row,6).value, price=sheet.cell(row,7).value, sell=sheet.cell(row,8).value,
                                expire=expire_str, tb_token='')
                            db.session.add(item)
                db.session.commit()
                os.remove('/home/lct/logs/tmp9s0d9.xls')
                return u'上传成功'
        return u'Hello'
    return redirect(url_for('security.login', next='/'))


@app.route('/search', methods=['GET'])
def api_search():
    catalog = request.args.get('catalog')
    activity = request.args.get('activity')
    offset = request.args.get('offset')
    if offset == None:
        offset = '0'
    offset = int(offset)
    limit = request.args.get('limit')
    if limit == None:
        limit = '20'
    limit = int(limit)
    rows = []
    if(activity == '0'):
        rows = GoodInfo.query.filter_by(catalog=catalog).order_by(GoodInfo.good_id.desc()).offset(offset).limit(limit).all()
    else:
        rows = GoodInfo.query.filter_by(activity=activity).order_by(GoodInfo.good_id.desc()).offset(offset).limit(limit).all()
    ret = []
    for row in rows:
        ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'sell': row.sell,
                    'price': row.price, 'url': row.url, 'off': row.off, 'rate': row.rate})
    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/query', methods=['GET'])
def api_query():
    id = request.args.get('id')
    rows = GoodInfo.query.filter_by(good_id=id).all()
    ret = []
    for row in rows:
        if row.tb_token==None or row.tb_token == '':
            ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'sell': row.sell,
                    'price': row.price, 'url': row.url, 'off': row.off, 'rate': row.rate, 'tb_token': ''})
        else:
            ret.append({'good_id': row.good_id, 'title': row.title, 'image': row.image, 'sell': row.sell,
                    'price': row.price, 'url': row.url, 'off': row.off, 'rate': row.rate, 'tb_token': row.tb_token})

    return jsonify({'status': 'ok',
                    'message': ret
                })


@app.route('/check', methods=['GET'])
def api_check():
    limit = 100
    offset = 0
    today = datetime.datetime.now().date()
    while True:
        rows = db.session.query(GoodInfo).offset(offset).limit(limit).all()
        offset = offset + limit
        if len(rows) == 0:
            break
        for row in rows:
            expire = datetime.datetime.strptime(row.expire, "%Y/%m/%d").date()
            if today > expire:
                item = OffGoodInfo(title=row.title, catalog=row.catalog, activity = row.activity,
                                    off=row.off, rate=row.rate, image=row.image,
                                    url=row.url, price=row.price, sell=row.sell,
                                    expire=row.expire)
                db.session.add(item)
                db.session.delete(row)
    db.session.commit();

    return jsonify({'status': 'ok',
                    'message': "OK"
                })


@app.route("/download", methods=['GET'])
def download_file():
    if not current_user.is_active or not current_user.is_authenticated:
        return redirect(url_for('security.login', next='/'))
    query_sets = OffGoodInfo.query.all()
    if query_sets == None:
        jsonify({'status': 'ok',
                    'message': "没有数据"
                })
    column_names = ['title', 'catalog', 'activity', 'off', 'rate', 'image', 'url', 'price', 'sell', 'expire']
    response = excel.make_response_from_query_sets(query_sets, column_names, "xls")
    cd = 'attachment; filename=expiredGood.xls'
    response.headers['Content-Disposition'] = cd
    db.session.query(OffGoodInfo).delete()
    db.session.commit()
    return response

# Create admin
admin = flask_admin.Admin(
    app,
    u'小牛快淘推荐商品后台管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)


# Add model views
#admin.add_view(MyModelView(Role, db.session))
#admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView2(GoodInfo, db.session))
admin.add_view(MyModelView2(OffGoodInfo, db.session))


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
    #context = ('/home/lct/user.server/sslcrts/2_shop.hanjianqiao.cn.crt', '/home/lct/user.server/sslcrts/3_shop.hanjianqiao.cn.key')
    #app.run(host='0.0.0.0', port=7009, ssl_context=context)
    app.run(host='0.0.0.0', port=7010, debug=True)
