# -*- coding: utf-8 -*- 
#!/usr/bin/env python
from flask import Flask, render_template, request, url_for, redirect, abort, session, g
import MySQLdb as mysqldb
import datetime
import config

app = Flask(__name__)
'''
这是一个匿名聊天的应用，闲心之作，应用了flask框架mysqldb等库写成
'''


@app.before_request			#在每次连接建立前，建立好与数据库的连接，并将连接保存到g.db上
def before_request():
    g.db = mysqldb.connect(host=config.HOST,user=config.USER,passwd=config.PASSWD,db=config.DB,port=coding.PORT,charset="utf8")

@app.teardown_request		#如果连接g.db建立了，在连接断开时关闭数据库的连接
def teardown_request(exception):
    if hasattr(g, 'db'):
		g.db.close()

@app.errorhandler(403)
def untouch(error):			#一个403非法登录的页面
	return """<p style="text-align:center">sorry,you must fill some information first</p>"""

@app.route("/")				#主页面
@app.route("/index/")
def index():
    return render_template("index.html",title="HOME")

@app.route("/login", methods=["GET","POST"])	#登录，建立session并重定向到chat页面
def login():
	if request.method == 'POST':
		session['username'] = unicode(request.form['nickname'])
		session['email'] = unicode(request.form['Email'])
		return redirect(url_for('chat'))
	else:
		return render_template("index.html",title="HOME",notify="open error")
@app.route("/loginout")							#退出登录
def loginout():
	session.pop('username')
	session.pop('email')
	return redirect(url_for('index'))

@app.route("/chat/")							#聊天室界面
@app.route("/chat/<war>")
def chat():
	if session['username'] and session['email']:
		username = session['username']
		email = session['email']
		#try:
		cur=g.db.cursor()
		cur.execute("select * from chats order by chat_id desc")				#从数据库中取出数据并显示到模板中
		items = [dict(user=row[1], email=row[2], mess=row[3], today=str(row[4])+" "+str(row[5])) for row in cur.fetchmany(100)]
		return render_template("chat.html",title="chat room",username=username,email=email,mess=items,logining=True)
	else:
		abort(403)
@app.route("/chat/add",methods=['POST'])
def chat_add():																								#添加数据
	if request.form['mess']=="" or request.form['mess']==None:
		return redirect(url_for('chat',war="不允许提交空表"))
	else:
		now=str(datetime.datetime.now())
		date=now[:10]
		time=now[11:19]
		values = [session['username'],session['email'],unicode(request.form['mess']),unicode(date),unicode(time)]
		cur=g.db.cursor()
		cur.execute("insert into chats(chat_user,chat_email,chat_mess,chat_date,chat_time) values(%s,%s,%s,%s,%s)",values)
		g.db.commit()
		return redirect(url_for('chat'))

app.secret_key = '\xb2\xc7\xe0\xa0\xe1c\x1a\xd1\x93D\xe7X\xde\x02\xd4\xbb+O\xbe+\x95.\xf7\xdd'

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80, debug=True)
