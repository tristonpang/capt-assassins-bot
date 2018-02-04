import requests, json, psycopg2, bcrypt, threading
from flask import Blueprint, request, render_template, redirect, make_response
from datetime import datetime
from private_vars import connStr

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')
hashLock = threading.Lock()
userHashes = set()

@adminEndpoints.route("/assassins/admin/")
def adminLoginPage():
    return render_template("admin-login.html", msg = request.args.get("msg"))

@adminEndpoints.route("/assassins/admin/login/", methods = ["POST"])
def adminLoginSubmit():
    if bcrypt.checkpw(str.encode(request.form['pw']), b'$2b$12$DWPryCWLqO9o6vpz4tITIuiU7MIjZatZaWPYulvP4x2XsFj/CodE2'):
        # Passed
        resp = make_response(redirect("/assassins/admin/dashboard"))
        # Create a hash
        userHash = bytes.decode(bcrypt.gensalt())
        with hashLock:
            # Add this hash to a set of authorised users, and attach this hash as a cookie to the response
            userHashes.add(userHash)
            resp.set_cookie('adminLoggedIn', userHash)
            return resp
    else:
        # Failed
        return redirect("/assassins/admin/?msg=Wrong+password")

@adminEndpoints.route("/assassins/admin/dashboard")
def adminIndex():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT u1.user_name AS Player, u1.user_nickname AS Nickname, t.task_description AS task, u2.user_name AS Target, u1.user_alive AS Status FROM users u1, users u2, tasks t, contracts c WHERE u1.user_id = c.contract_assid AND u2.user_id = contract_targetid AND c.contract_taskid = t.task_id")
    data = cur.fetchall()
    cur.close()
    return render_template("admin-info.html", data=data)


@adminEndpoints.route("/assassins/addplayer")
def displayAdmin():
    return render_template("admin-add.html")

@adminEndpoints.route("/assassins/editplayer")
def displayEdit():
    return render_template("admin-edit.html")

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
    print(request.form)
    cur.execute("UPDATE users"
                "SET (user_status, user_task, user_target) VALUES (alive, %s, %s)"
                "WHERE (user_password) VALUES (%s)",
                (request.form['task'], request.form['target'], request.form['token']))
    cur.close()
    return render_template("admin-success.html")

# To be done after editing conn.
# @adminEndpoints.route("/assassins/admin/editplayersubmit", methods=['POST'])
# def displayEditSuccess():
#     cur = conn.cursor()
#     print(request.form)
#     cur.execute("UPDATE users"
#                 "SET (user_password, user_name, user_nickname, user_target, ) VALUES (alive, %s, %s)"
#                 "WHERE (user_password) VALUES (%s)",
#                 (request.form['task'], request.form['target'], request.form['token']))
#     conn.commit()
#     return render_template("admin-deletesuccess.html")
