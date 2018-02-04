import requests, json
from flask import Blueprint, request, render_template
import psycopg2
from datetime import datetime
from private_vars import connStr

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')


@adminEndpoints.route("/assassins/admin")
def adminIndex():
	conn = psycopg2.connect(connStr)
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute("SELECT u1.user_name AS Player, u1.user_nickname AS Nickname, c.contracts_task AS task, u2.user_name AS Target, u1.user_alive AS Status FROM users u1, users u2, tasks t, contracts c WHERE u1.user_id = c.contract_assid AND u2.user_id = contract_targetid AND c.contract_taskid = t.task_id")
	data = cur.fetchall()
	cur.close()
	return render_template("admin-info.html", data=data)


@adminEndpoints.route("/assassins/addplayer")
def displayAdmin():
	return render_template("admin-add.html")

@adminEndpoints.route("/assassins/deleteplayer")
def displaydelete():
	return render_template("admin-delete.html")

@adminEndpoints.route("/assassins/reviveplayer")
def displayRevive():
	return render_template("admin-revive.html")

@adminEndpoints.route("/assassins/admin/addplayersubmit", methods=['POST'])
def displaySubmit():
	conn = psycopg2.connect(connStr)
	conn.autocommit = True
	cur = conn.cursor()
	print(request.form)
	cur.execute("INSERT into users (user_nickname, user_name, user_password) VALUES (%s, %s, %s)",
				(request.form['nickname'], request.form['name'], request.form['token']))
	# # cur.execute("INSERT into contracts (contracts_task, contract_assid) VALUES (%s, %s) WHERE contract_assid = (SELECT user_id FROM users WHERE user_password = %s)", ([request.form['task']], request.form['token']))
	cur.execute("SELECT MAX(user_id) FROM users")
	tempMaxId = cur.fetchone();
	maxId = tempMaxId[0];

	cur.execute("SELECT user_id FROM users WHERE user_name = %s", [request.form['target']])
	tempTarget = cur.fetchone();
	target = tempTarget[0];

	print(maxId)
	print(target)

	cur.execute("INSERT into contracts (contract_assid, contract_targetid, contracts_task, contract_taskid) VALUES (%s, %s, %s, 1)", [maxId, target, request.form['task']])

	cur.close()
	return render_template("admin-success.html")

@adminEndpoints.route("/assassins/admin/deleteplayersubmit", methods=['POST'])
def displayDelSuccess():
	conn = psycopg2.connect(connStr)
	conn.autocommit = True
	cur = conn.cursor()
	print(request.form)
	cur.execute("DELETE FROM users WHERE user_password = %s", (request.form['exampleInputToken']))
	cur.close()
	return render_template("admin-deletesuccess.html")

@adminEndpoints.route("/assassins/admin/reviveplayersubmit", methods=['POST'])
def displayReviveSuccess():
	conn = psycopg2.connect(connStr)
	conn.autocommit = True
	cur = conn.cursor()
	# String of target in var
	target = request.form['target'] 
	# cur.execute("SELECT FROM users WHERE user_name = %s", target)
	
	cur.execute("UPDATE users SET user_alive = true WHERE user_password = %s", ([request.form['token']]))
  
	print(request.form)
	cur.close()
	return render_template("admin-success.html")

# To be done after deleteing conn.
# @adminEndpoints.route("/assassins/admin/deleteplayersubmit", methods=['POST'])
# def displaydeleteSuccess():
#     cur = conn.cursor()
#     print(request.form)
#     cur.execute("UPDATE users"
#                 "SET (user_password, user_name, user_nickname, user_target, ) VALUES (alive, %s, %s)"
#                 "WHERE (user_password) VALUES (%s)",
#                 (request.form['task'], request.form['target'], request.form['token']))
#     conn.commit()
#     return render_template("admin-deletesuccess.html")
