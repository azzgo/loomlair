loomlair
========

a flask app
更换使用了pure前端框架

在使用之前确保安装了flask-login,flask-wtf,flask-sqlachedemy扩展

并在测试时在项目目录下创建 dev-config

其内容为

SQLALCHEMY_DATABASE_URI = '你的mysql地址'
SECRET_KEY = '你的密匙'
WTF_CSRF_ENABLED = False

运行前先运行

```
fab initial
```

初始化数据库

然后运行

```
fab dev
```

测试程序