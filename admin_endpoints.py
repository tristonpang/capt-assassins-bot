import requests, json
from flask import Blueprint, request, render_template
import psycopg2
from datetime import datetime
from private_vars import conn

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')

@adminEndpoints.route("/assassins/admin")
def adminIndex():
    return render_template("admin-info.html")

@adminEndpoints.route("/assassins/admin/addplayers")
def displayAdmin():
	
	return render_template("admin-add.html")

@adminEndpoints.route("/assassins/admin/addplayersubmit", methods = ['POST'])
def displaySubmit():
	cur = conn.cursor()
	print(request.form)
	cur.execute("INSERT into users (user_nickname, user_name, user_password) VALUES (%s, %s, %s)", (request.form['nickname'], request.form['name'], request.form['token']))
	conn.commit()
	return render_template("admin-success.html")