import requests, json
from flask import Blueprint, request, render_template, redirect
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, connStr
import random
from telegram import sendMsg, fetchStatus

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
    pending_confirmation = False

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
        cur.execute("SELECT contracts.contracts_task, users.user_name, contracts.contract_pending_confirm FROM contracts \
        INNER JOIN users ON users.user_id = contracts.contract_targetID WHERE \
        contracts.contract_complete is null and contracts.contract_assID = %s", (user_id,))
        task_data = cur.fetchone()
        if task_data is not None:
            pending_confirmation = task_data[2]
            task_desc = task_data[0]
            target_name = task_data[1]
        else:
            task_desc = None
            target_name = None
    
    cur.close()

    #slice data, add into return statement
    return render_template("player-info.html", token = token, user_alive = user_alive, 
        user_nick = user_nickname, user_name = user_name, task = task_desc, target = target_name, user_hash = user_hash, 
        pending_confirmation = pending_confirmation, msg = request.args.get("msg"))

@usersEndpoints.route("/assassins/<token>/kill/")
def killPage(token):
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT user_id, user_name FROM users WHERE user_password = %s", (token,))
    player = cur.fetchone()
    if player is not None:
        cur.execute("UPDATE contracts SET contract_pending_confirm = true where \
        contract_complete is null and contract_assid = %s", (player[0],))
        # Message the game masters
        sendMsg(272553166, "An assassination attempt by "+player[1]+" has been logged. Please check the [admin dashboard](https://yenter.io/assassins/admin/dashboard/)!")
        sendMsg(378439213, "An assassination attempt by "+player[1]+" has been logged. Please check the [admin dashboard](https://yenter.io/assassins/admin/dashboard/)!")
        return redirect("/assassins/" + token + "/?msg=You+have+assassinated+your+target.")
