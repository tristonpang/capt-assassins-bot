import requests, json, psycopg2, bcrypt
from flask import Blueprint, request, render_template, redirect, make_response
from datetime import datetime
from private_vars import connStr

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')

def loggedIn():
    userHash = request.cookies.get("adminLoggedIn")
    if userHash is None:
        return False
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT id FROM admin_users WHERE hash = %s", (userHash,))
    if cur.fetchone() is None:
        return False
    else:
        return True


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
        # Add this hash to a set of authorised users, and attach this hash as a cookie to the response
        conn = psycopg2.connect(connStr)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO admin_users (hash) VALUES (%s)", (userHash,))
        resp.set_cookie('adminLoggedIn', userHash)
        return resp
    else:
        # Failed
        return redirect("/assassins/admin/?msg=Wrong+password")

@adminEndpoints.route("/assassins/admin/logout/")
def adminLogout():
    userHash = request.cookies.get("adminLoggedIn")
    if userHash is not None:
        conn = psycopg2.connect(connStr)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DELETE FROM admin_users WHERE hash = %s", (userHash,))
    return redirect("/assassins/admin/")

@adminEndpoints.route("/assassins/admin/dashboard")
def adminIndex():

    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT u1.user_name AS Player, u1.user_nickname AS Nickname, c.contracts_task AS task, u2.user_name AS Target, u1.user_alive AS Status FROM users u1, users u2, contracts c WHERE u1.user_id = c.contract_assid AND u2.user_id = c.contract_targetid")
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
    cur.execute("SELECT MAX(user_id) FROM users")
    tempMaxId = cur.fetchone();
    maxId = tempMaxId[0];

    cur.execute("SELECT user_id FROM users WHERE user_name = %s", [request.form['target']])
    tempTarget = cur.fetchone();
    target = tempTarget[0];

    print(maxId)
    print(target)

    cur.execute("INSERT into contracts (contract_assid, contract_targetid, contracts_task) VALUES (%s, %s, %s)", [maxId, target, request.form['task']])

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

    cur.execute("SELECT user_id FROM users WHERE user_password = %s", [request.form['token']])
    tempToken = cur.fetchone();
    token = tempToken[0];

    cur.execute("SELECT user_id FROM users WHERE user_name = %s", [request.form['target']])
    tempTarget = cur.fetchone();
    target = tempTarget[0];

    cur.execute("INSERT INTO contracts (contract_assid, contract_targetid, contracts_task) VALUES (%s, %s, %s)", [token, target, request.form['task']])

    print(token)
    print(target)
    print(request.form['task'])
    cur.close()
    return render_template("admin-success.html")

@adminEndpoints.route("/assassins/admin/editplayersubmit", methods=['POST'])
def displayEditSuccess():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    print(request.form)

    cur.execute("SELECT user_id FROM users WHERE user_password = %s", [request.form['token']])
    tempToken = cur.fetchone();
    token = tempToken[0];

    cur.execute("SELECT user_id FROM users WHERE user_name = %s", [request.form['target']])
    tempTarget = cur.fetchone();
    target = tempTarget[0];

    cur.execute("UPDATE users SET (user_name, user_nickname) VALUES (%s, %s) WHERE user_id = %s", (request.form['name'], request.form['nickname', token]))

    cur.execute("DELETE FROM contracts WHERE contract_assid = %s", (token))
    cur.execute("INSERT INTO contracts (contract_assid, contract_asstargetid, contracts_task) VALUES (token, target, request.form['task'])")

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
