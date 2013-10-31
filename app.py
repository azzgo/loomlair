#!/usr/bin/env python
from flask import Flask, render_template, request, url_for, redirect, abort, session
import MySQLdb as mysqldb
import datetime
def coldb(insertmes):
	try:
		conn=mysqldb.connect(host='localhost',user='root',passwd='90243719',db='chatrow',port=3306)
		cur=conn.cursor()
		cur.execute(insertmes)
		conn.commit()
		cur.close()
		conn.close()
		return
	except mysqldb.Error,e:
		return "Mysql Error %d: %s" % (e.args[0], e.args[1])


app = Flask(__name__)
@app.errorhandler(403)
def untouch(error):
	return """<p style="text-align:center">sorry,you must fill some information first</p>"""

@app.route("/")
@app.route("/index/")
def index():
    return render_template("index.html",title="HOME")

@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == 'POST':
		session['username'] = str(request.form['nickname'])
		session['email'] = str(request.form['Email'])
		return redirect(url_for('chat'))
	else:
		return render_template("index.html",title="HOME",notify="open error")
@app.route("/loginout")
def loginout():
	session.pop('username')
	session.pop('email')
	return redirect(url_for('index'))

@app.route("/chat/")
def chat():
	if session['username'] and session['email']:
		username = session['username']
		email = session['email']
		#try:
		conn=mysqldb.connect(host='localhost',user='root',passwd='90243719',db='chatrow',port=3306)
		cur=conn.cursor()
		cur.execute("select * from chats order by chat_id desc")
		items = [dict(user=row[1], email=row[1], mess=row[2], today=row[3]) for row in cur.fetchmany(5)]
		cur.close()
		conn.close()
		return render_template("chat.html",title="chat room",username=username,email=email,mess=items,logining=True)
		#except:
		#	abort(405)
	else:
		abort(403)
@app.route("/chat/add",methods=['POST'])
def chat_add():
	#try:
	values = [session['username'],session['email'],request.form['mess'],str(datetime.date.today())]
	conn=mysqldb.connect(host='localhost',user='root',passwd='90243719',db='chatrow',port=3306)
	cur=conn.cursor()
	cur.execute("insert into chats(chat_user,chat_email,chat_mess,chat_time) values(%s,%s,%s,%s)",values)
	conn.commit()
	cur.close()
	conn.close()
#	except:
#		pass
	return redirect(url_for('chat'))

app.secret_key = '\xb2\xc7\xe0\xa0\xe1c\x1a\xd1\x93D\xe7X\xde\x02\xd4\xbb+O\xbe+\x95.\xf7\xdd'

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80, debug=True)

