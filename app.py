# -*- coding: utf-8 -*-
#!/usr/bin/env python
from flask import (
  Flask,
  render_template,
  request,
  url_for,
  redirect,
  abort,
  session,
  flash,
  jsonify,
  g)
from flask.json import JSONEncoder
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# jsonify设置
class CustomEncoder(JSONEncoder):
    """
    定制jsonify 额外类型的支持
    """
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, (Chat, OnlineUser)):
            return obj.to_json()
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomEncoder

# app配置
app.config.from_envvar('ENV')

# 配置数据库
db = SQLAlchemy(app)

# 用户数据类
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nickname = db.Column(db.String(80), unique=True)
  email = db.Column(db.String(120), unique=True)

  def __init__(self, nickname, email):
    self.nickname = nickname
    self.email = email

  def is_authenticated(self):
        return True

  def is_active(self):
      return True

  def is_anonymous(self):
      return False

  def get_id(self):
      return unicode(self.id)

# 发送的消息数据类
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80))
    content = db.Column(db.Text())
    pub_time = db.Column(db.DateTime)

    def __init__(self, nickname, content):
        self.nickname = nickname
        self.content = content
        self.pub_time =  datetime.datetime.now()

    def to_json(self):
        return {
            'nickname': self.nickname,
            'content': self.content,
            'pub_time': self.pub_time
        }

# 记录在线人数数据类
class OnlineUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80))
    dead_time = db.Column(db.DateTime)

    def __init__(self, nickname):
        self.nickname = nickname
        self.dead_time = datetime.datetime.now() + datetime.timedelta(minutes = 30)

    def to_json(self):
        return {'nickname': self.nickname}

# 表单验证设置
from flask_wtf import Form
from wtforms import StringField
from wtforms import validators

class UserForm(Form):
  nickname = StringField('nickname', validators=[validators.InputRequired(), validators.Length(min=3, message=u"最少需要三位")])
  email =  StringField('email', validators=[validators.InputRequired(), validators.Email(message=u"Email 格式不对")])

# 用户登陆设置
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))
#url 页面处理
@app.route("/")
def index():
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  return redirect(url_for('chat'))

# 登录
@app.route("/login/", methods=["POST"])
def login():
    form  = UserForm()
    if form.validate_on_submit():
        nickname = form.data['nickname']
        email = form.data['email']
        user = User.query.filter_by(nickname=nickname).first()
        if user and user.email == email:
            login_user(user)
        elif user and user.email != email:
            flash([[u"用户已经存在"]])
            return render_template("login.html",title=u"登陆")
        else:
            user = User(nickname, email)
            db.session.add(user)
        db.session.add(OnlineUser(nickname))
        return redirect(url_for('chat'))
    flash(form.errors.values())
    return render_template("login.html",title=u"登陆")

@app.route("/login/", methods=["GET"])
def login_page():
    return render_template("login.html",title=u"登陆")

# 退出登录
@app.route("/logout/")
@login_required
def loginout():
    user = OnlineUser.query.filter_by(nickname=current_user.nickname).first()
    db.session.delete(user)
    logout_user()
    return redirect(url_for('index'))

# 聊天室界面
@app.route("/chat/")
@login_required
def chat():
    return render_template("chat.html", user=current_user)

# 添加数据
@app.route("/chat/add/",methods=['POST'])
def chat_add():
    nickname = current_user.nickname
    content = request.form.get('message')
    if content is None:
        abort(403)
    chat = Chat(nickname, content)
    db.session.add(chat)
    return '',201

# 获取数据
@app.route('/chat/get/',methods=["GET"])
def chat_get():
    try:
        last_time = session.get('last_time', datetime.datetime.now())
        nickname = current_user.nickname
        msg = Chat.query.filter('pub_time > :last_time').params(last_time=last_time).all()
        if len(msg) != 0:
            session['last_time'] = datetime.datetime.now()
        return jsonify(msg=msg)
    except AttributeError:
        abort(401)

# 获取在线用户数据
@app.route('/chat/userlist/get/', methods=["GET"])
def chat_user_get():
    userlist = OnlineUser.query.filter('dead_time < :now').params(now=datetime.datetime.now()).all()
    map(db.session.delete, userlist)
    db.session.commit()
    userlist = OnlineUser.query.all()
    return jsonify(userlist=userlist)

# 请求代码
@app.before_request
def before_request():
    if current_user.is_active():
        user = OnlineUser.query.filter_by(nickname=current_user.nickname).first()
        user.dead_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    g.db = db

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.session.commit()

@app.errorhandler(404)
def not_findpage(error):
    return render_template("404.html"),404

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
