#!/usr/bin/python
from fabric.api import local

def dev():
    local('ENV=./dev-config.cfg python app.py')

def initial():
    local('ENV=./dev-config.cfg python -c "from app import db;db.create_all()"')