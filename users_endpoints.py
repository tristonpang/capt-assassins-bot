import requests, json
from flask import Blueprint, request, render_template
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, conn

# from flask_cache import Cache

usersEndpoints = Blueprint('usersEndpoints', __name__, template_folder='templates')

@usersEndpoints.route("/assassins/")
def index():
    return render_template("player-login.html")

@usersEndpoints.route("/assassins/<token>")
def displayPage(token):
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_nickname, user_name, user_alive, user_telegram FROM users WHERE user_password = %s", (token,))
    user_data = cur.fetchone()
    
    user_id = user_data[0]
    user_nickname = user_data[1]
    user_name = user_data[2]
    user_alive = user_data[3]
    user_telegram = user_data[4]

    if user_telegram is None:
        # User has not yet added their telegram
        # Ask them to do so
        return render_template("player-info.html", request_tele = True, user_nick = user_nickname)
    else:
        if not user_alive:
            task_desc = None
            target_name = None
        else:
            cur.execute("SELECT tasks.task_description, users.user_name FROM contracts INNER JOIN tasks ON tasks.task_id = \
            contracts.contract_taskID INNER JOIN users ON users.user_id = contracts.contract_targetID WHERE \
            contracts.contract_complete is null and contracts.contract_assID = %s", (user_id,))
            task_data = cur.fetchone()
            task_desc = task_data[0]
            target_name = task_data[1]

        #slice data, add into return statement
        return render_template("player-info.html", token = token, user_alive = user_alive, 
            user_nick = user_nickname, user_name = user_name, task = task_desc, target = target_name, request_tele = False)

@usersEndpoints.route("/assassins/<token>/kill")
def killPage(token):
    cur = conn.cursor()
    cur.execute("SELECT users.user_id, contracts.contract_id, contract_targetID \
        FROM users INNER JOIN contracts ON users.user_id = contracts.contract_assId \
        WHERE contracts.contract_complete is null and users.user_password = %s", (token,))
    data = cur.fetchone()
    user_id = data[0]
    contract_id = data[1]
    target_id = data[2]
    cur.execute("UPDATE users SET user_alive = FALSE WHERE user_id = %s", (target_id,))
    # conn.commit()
    cur.execute("UPDATE contracts SET contract_complete = now() WHERE contract_id = %s", (contract_id,))
    # conn.commit()
    cur.execute("UPDATE contracts SET contract_assID = %s WHERE contract_assID = %s", (user_id, target_id))
    # conn.commit()
    #set target's status to dead
    #set user's new target and task
    cur.execute("SELECT user_name FROM users WHERE user_id = %s", (target_id,))
    old_target_name = cur.fetchone()[0]
    return render_template("player-killconfirmed.html", dead_target = old_target_name)