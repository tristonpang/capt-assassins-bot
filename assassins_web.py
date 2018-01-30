from flask import Flask, render_template, url_for, request, redirect, Response, jsonify
import psycopg2

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

conn = psycopg2.connect("host=localhost dbname=assassins user=assassins password=captslock")

app = Flask(__name__)
#cache = Client(('https://yenter.io/', 11211))

@app.route("/assassins/")
def index():
    return render_template("player-login.html")

@app.route("/assassins/<token>")
def displayPage(token):
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_nickname, user_name FROM users WHERE user_password = %s", (token,))
    user_data = cur.fetchone()
    
    user_id = user_data[0]
    user_nickname = user_data[1]
    user_name = user_data[2]
    cur.execute("SELECT tasks.task_description, users.user_name FROM contracts INNER JOIN tasks ON tasks.task_id = \
        contracts.contract_taskID INNER JOIN users ON users.user_id = contracts.contract_targetID WHERE contracts.contract_assID = %s", (user_id,))
    task_data = cur.fetchone()
    task_desc = task_data[0]
    target_name = task_data[1]

    #slice data, add into return statement
    return render_template("player-info.html", usernick = user_nick, username = user_name, task = task_desc, target = target_name)

@app.route("/assassins/<token>/kill")
def killPage(token):
    cur = conn.cursor()
    cur.execute("SELECT contract_id, contract_targetID, contract_taskID FROM contracts WHERE contract_assId = %s", (token,))
    data = cur.fetchone()
    target_id = data[0]
    next_target_id = data[1] 
    next_task_id = data[2]
    cur.execute("UPDATE users SET user_alive = FALSE WHERE user_id = %s", (target_id,))
    cur.execute("UPDATE contracts SET contract_targetID = %s, contract_taskID = %s WHERE contract_id = %s", (next_target_id, next_task_id, token))
    #set target's status to dead
    #set user's new target and task
    cur.execute("SELECT user_name FROM users WHERE user_id = %s", (target_id,))
    old_target_name = cur.fetchone()[0]
    return render_template("player-killconfirmed.html", dead_target = old_target_name)

if __name__ == "__main__":
    app.run(debug = True)