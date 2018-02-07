import requests, json
from flask import Blueprint, request, render_template, redirect
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, connStr
import random
from telegram import sendMsg, fetchStatus

# from flask_cache import Cache

usersEndpoints = Blueprint('usersEndpoints', __name__, template_folder='templates')

@usersEndpoints.route("/assassins/")
def index():
    return render_template("player-login.html", msg = request.args.get("msg"))

@usersEndpoints.route("/assassins/<token>/")
def displayPage(token):
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_nickname, user_name, user_alive, user_telegram FROM users WHERE user_password = %s", (token,))
    user_data = cur.fetchone()
    
    if user_data is None:
        # User not found
        return redirect("/assassins/?msg=Token+not+found")
    user_id = user_data[0]
    user_nickname = user_data[1]
    user_name = user_data[2]
    user_alive = user_data[3]
    user_telegram = user_data[4]
    user_hash = None

    if user_telegram is None:
        # User has not yet added their telegram
        # Ask them to do so
        # Generate random hash to associate with this user
        # Store in table
        user_hash = "%032x" % random.getrandbits(128)
        cur.execute("INSERT INTO tele_ids (user_id, tele_hash) VALUES (%s, %s) ON CONFLICT \
        (user_id) DO UPDATE SET tele_hash = excluded.tele_hash", (user_id, user_hash))

    if not user_alive:
        task_desc = None
        target_name = None
    else:
        cur.execute("SELECT contracts.contracts_task, users.user_name FROM contracts \
        INNER JOIN users ON users.user_id = contracts.contract_targetID WHERE \
        contracts.contract_complete is null and contracts.contract_assID = %s", (user_id,))
        task_data = cur.fetchone()
        if task_data is not None:
            task_desc = task_data[0]
            target_name = task_data[1]
        else:
            task_desc = None
            target_name = None
    
    cur.close()

    #slice data, add into return statement
    return render_template("player-info.html", token = token, user_alive = user_alive, 
        user_nick = user_nickname, user_name = user_name, task = task_desc, target = target_name, user_hash = user_hash, 
        msg = request.args.get("msg"))

@usersEndpoints.route("/assassins/<token>/kill/")
def killPage(token):
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT users.user_id, contracts.contract_id, contract_targetID, users.user_nickname, \
        users.user_telegram FROM users INNER JOIN contracts ON users.user_id = contracts.contract_assId \
        WHERE contracts.contract_complete is null and users.user_password = %s", (token,))
    data = cur.fetchone()
    user_id = data[0]
    contract_id = data[1]
    target_id = data[2]
    user_nickname = data[3]
    user_telegram = data[4]

    cur.execute("UPDATE users SET user_alive = FALSE WHERE user_id = %s", (target_id,))
    cur.execute("UPDATE contracts SET contract_complete = now() WHERE contract_id = %s", (contract_id,))
    cur.execute("UPDATE contracts SET contract_assID = %s WHERE contract_assID = %s", (user_id, target_id))
    #set target's status to dead
    #set user's new target and task
    # cur.execute("SELECT user_name, user_telegram FROM users WHERE user_id = %s", (target_id,))
    # data = cur.fetchone()
    # old_target_name = data[0]
    # target_chat_id = data[1]

    currStatus = fetchStatus(cur) # get the current status
    cur.execute("SELECT user_id, user_name, user_telegram FROM users WHERE user_telegram IS NOT NULL")
    telegramIDs = cur.fetchall()

    for teleUser in telegramIDs:
        if teleUser[0] == target_id:
            sendMsg(teleUser[1], "*Oh no!* You have been killed by _" + user_nickname + "_!")
        else:
            sendMsg(teleUser[1], "_There has been an assassination._")
        sendMsg(teleUser[1], currStatus)
    
    cur.close()

    return redirect("/assassins/" + token + "/?msg=You+have+assassinated+your+target.")