import requests, json
from flask import Blueprint, request, render_template
import psycopg2
from datetime import datetime
from private_vars import conn

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')


@adminEndpoints.route("/assassins/admin")
def adminIndex():
    cur = conn.cursor()
    cur.execute("SELECT u1.user_name AS Player, u1.user_nickname AS Nickname, t.task_description AS task, u2.user_name AS Target, u1.user_alive AS Status FROM users u1, users u2, tasks t, contracts c WHERE u1.user_id = c.contract_assid AND u2.user_id = contract_targetid AND c.contract_taskid = t.task_id")
    data = cur.fetchall()
    return render_template("admin-info.html", data=data)


@adminEndpoints.route("/assassins/addplayer")
def displayAdmin():
    return render_template("admin-add.html")

@adminEndpoints.route("/assassins/deleteplayer")
def displayDelete():
    return render_template("admin-delete.html")


@adminEndpoints.route("/assassins/admin/addplayersubmit", methods=['POST'])
def displaySubmit():
    cur = conn.cursor()
    print(request.form)
    cur.execute("INSERT into users (user_nickname, user_name, user_password) VALUES (%s, %s, %s)",
                (request.form['nickname'], request.form['name'], request.form['token']))
    conn.commit()
    return render_template("admin-success.html")

@adminEndpoints.route("/assassins/admin/deleteplayersubmit", methods=['POST'])
def displayDelSuccess():
    cur = conn.cursor()
    print(request.form)
    cur.execute("DELETE FROM users WHERE user_password = %s", (request.form['exampleInputToken']))
    conn.commit()
    return render_template("admin-deletesuccess.html")

@adminEndpoints.route("/assassins/reviveplayer", methods=['POST'])
def displayRevive():
    return render_template("admin-revive.html")


@adminEndpoints.route("/assassins/reviveplayersubmit", methods=['POST'])
def displayReviveSuccess():
    cur = conn.cursor()
    print(request.form)
    cur.execute("UPDATE users"
                "SET (user_status, user_task, user_target) VALUES (alive, %s, %s)"
                "WHERE (user_password) VALUES (%s)",
                (request.form['task'], request.form['target'], request.form['token']))
    conn.commit()
    return render_template("admin-success.html")
