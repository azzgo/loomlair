#!/usr/bin/env python
from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
@app.route("/index/")
def index():
    return render_template("index.html",title="HOME")

@app.route("/login", methods="GET")
def login():
    pass

@app.route("/chat/")
def chat():
    return render_template("chat.html",title="chat room")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80, debug=True)

