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
    if loggedIn():
        return redirect("/assassins/admin/dashboard/")
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

@adminEndpoints.route("/assassins/admin/dashboard/")
def adminIndex():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT users.user_name, users.user_nickname, users.user_password, \
    users.user_alive, count(contracts.contract_complete) as numKills \
    FROM users LEFT JOIN contracts ON users.user_id = contracts.contract_assid \
    GROUP BY users.user_id ORDER BY users.user_alive DESC, numKills DESC, users.user_name")
    users = cur.fetchall()


    cur.execute("SELECT u1.user_name AS Player, u1.user_nickname AS Nickname, \
    c.contracts_task AS task, u2.user_name, u2.user_nickname, c.contract_complete FROM users u1, \
    users u2, contracts c WHERE u1.user_id = c.contract_assid AND u2.user_id = c.contract_targetid\
    ORDER BY c.contract_complete DESC")
    contracts = cur.fetchall()
    cur.close()

    completedContracts = []
    upcomingContracts = []

    for contract in contracts:
        if contract[5] is None:
            # Not completed yet
            upcomingContracts.append(contract)
        else:
            # Completed
            contract = list(contract)
            contract[5] = contract[5].strftime("%a %d %b, %I:%M %p")
            # contract[5] = 
            completedContracts.append(contract)

    return render_template("admin-info.html", upcoming = upcomingContracts, completed = completedContracts, success = request.args.get("success"),
                           users = users)

@adminEndpoints.route("/assassins/admin/addplayer/")
def displayAddPlayer():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name, user_nickname FROM users ORDER BY user_name")
    data = cur.fetchall()
    cur.close()
    return render_template("admin-add.html", data=data, success = request.args.get("success"))

@adminEndpoints.route("/assassins/admin/editplayer/")
def displayEdit():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name, user_nickname FROM users ORDER BY user_name")
    data = cur.fetchall()
    cur.close()
    return render_template("admin-edit.html", users = data, success = request.args.get("success"))

@adminEndpoints.route("/assassins/admin/deleteplayer/")
def displayDelete():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name, user_nickname FROM users ORDER BY user_name")
    data = cur.fetchall()
    cur.close()
    return render_template("admin-delete.html", users = data, success = request.args.get("success"))

@adminEndpoints.route("/assassins/admin/searchUser/<userID>/")
def searchUser(userID):
    if not loggedIn():
        return json.dumps({"status": "not-authorised"})
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT users.user_nickname, users.user_password, \
    users.user_name \
    FROM users WHERE users.user_id = %s ", (userID,))
    data = cur.fetchone()

    cur.execute("SELECT contract_targetid, contracts_task FROM contracts WHERE \
    contract_assid = %s AND contract_complete IS NULL", (userID,))
    task = cur.fetchone()
    cur.close()

    resp = {"status": "ok", "data": {
        "nickname": data[0],
        "token": data[1],
        "name": data[2]
        # "targetID": data[3], # null if no task
        # "task": data[4] # null if no task
    }}

    if task is not None:
        resp["data"]["targetID"]= task[0]
        resp["data"]["task"] = task[1]
    else:
        resp["data"]["targetID"] = None
        resp["data"]["task"] = None

    return json.dumps(resp)

@adminEndpoints.route("/assassins/admin/reviveplayer/")
def displayRevive():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name, user_nickname FROM users WHERE user_alive = 'f' ORDER BY user_name")
    reviveData = cur.fetchall()

    cur.execute("SELECT user_id, user_name, user_nickname, user_alive FROM users ORDER BY user_alive DESC, user_name")
    data = cur.fetchall()
    cur.close()

    return render_template("admin-revive.html", deadplayer = reviveData, data = data, success = request.args.get("success"))

@adminEndpoints.route("/assassins/admin/addplayersubmit/", methods=['POST'])
def displayAddSuccess():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    print(request.form)
    cur.execute("INSERT into users (user_nickname, user_name, user_password) VALUES (%s, %s, %s)",
                (request.form['nickname'], request.form['name'], request.form['token']))
    cur.execute("SELECT MAX(user_id) FROM users")
    tempMaxId = cur.fetchone()
    maxId = tempMaxId[0]
    print(request.form['user_id'])

    cur.execute("INSERT into contracts (contract_assid, contract_targetid, contracts_task) VALUES (%s, %s, %s)",
                (maxId, request.form['user_id'], request.form['task']))

    cur.close()
    return redirect("/assassins/admin/addplayer?success=Successfully+added+player!")

@adminEndpoints.route("/assassins/admin/deleteplayersubmit/", methods=['POST'])
def displayDelSuccess():
    if not loggedIn():
        return redirect("/assassins/admin/?msg=Please+log+in")
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM contracts WHERE contract_assid = %s OR contract_targetid = %s", (request.form['user_id'], request.form['user_id']))
    cur.execute("DELETE FROM users WHERE user_id = %s", ([request.form['user_id']]))
    cur.close()
    return redirect("/assassins/admin/deleteplayer?success=Successfully+deleted+player!")

@adminEndpoints.route("/assassins/admin/reviveplayersubmit/", methods=['POST'])
def displayReviveSuccess():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    # String of target in var
    # cur.execute("SELECT FROM users WHERE user_name = %s", target)
    cur.execute("UPDATE users SET user_alive = true WHERE user_id = %s", ([request.form['user_id']]))
    token = request.form['user_id']
    target = request.form['target_id']
    cur.execute("INSERT INTO contracts (contract_assid, contract_targetid, contracts_task) VALUES (%s, %s, %s)",
                [token, target, request.form['task']])
    cur.close()
    return redirect("/assassins/admin/reviveplayer?success=Successfully+revived+player!")

@adminEndpoints.route("/assassins/admin/editplayersubmit/", methods=['POST'])
def displayEditSuccess():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    print(request.form)

    # cur.execute("SELECT user_id FROM users WHERE user_password = %s", [request.form['token']])
    # tempToken = cur.fetchone()
    # token = tempToken[0]

    # cur.execute("SELECT user_id FROM users WHERE user_name = %s", [request.form['target']])
    # tempTarget = cur.fetchone()
    # target = tempTarget[0]

    cur.execute("UPDATE users SET user_password = %s, user_name = %s, user_nickname = %s WHERE user_id = %s",
                (request.form['token'], request.form['name'], request.form['nickname'], request.form['user_id']))

    cur.execute("DELETE FROM contracts WHERE contract_assid = %s AND contract_complete is NULL", (request.form['user_id'],))
    cur.execute("INSERT INTO contracts (contract_assid, contract_targetid, contracts_task) \
    VALUES (%s, %s, %s)", [request.form['user_id'], request.form['target'], request.form['task']])

    cur.close()
    # return render_template("admin-success.html")
    return redirect("/assassins/admin/editplayer?success=Successfully+edited+player!")

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
