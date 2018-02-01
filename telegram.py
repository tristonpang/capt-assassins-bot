import requests, json
from flask import Blueprint, request
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, conn

# from flask_cache import Cache

ids = set()

teleBot = Blueprint('teleBot', __name__, template_folder='templates')

# cache = SimpleCache()
# cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/'})

@teleBot.route('/assassins/telegram/update/', methods = ["POST"])
def telegramUpdate():
    data = request.get_json()
    chatID = data["message"]["chat"]["id"]
    if chatID not in ids:
        ids.add(chatID)
    if "text" in data["message"] and data["message"]["text"][0:7] == "/status":
        # Send update
        print("Received status update request")
        # Fetch status
        cur = conn.cursor()
        cur.execute("SELECT users.user_nickname, users.user_alive, count(contracts.contract_complete) FROM users LEFT JOIN contracts ON users.user_id = contracts.contract_assid GROUP BY users.user_id ORDER BY users.user_alive DESC, users.user_nickname")
        users = cur.fetchall()
        outputStr = "*Current Players*\n"
        for user in users:
            userData = user[0] + " ("
            if user[2] != 1:
                userData += str(user[2])+" kills"
            else:
                userData += "1 kill"
            userData += ")"
            if user[1]:
                outputStr += userData + "\n"
            else:
                outputStr += "_" + userData + " - dead_\n"
        outputStr += "\n*Completed Contracts*\n"
        cur.execute("SELECT assassin.user_nickname, target.user_nickname, tasks.task_description, \
        contracts.contract_complete FROM contracts INNER JOIN users AS assassin ON \
        contracts.contract_assid = assassin.user_id INNER JOIN users AS target ON \
        contracts.contract_targetid = target.user_id INNER JOIN tasks ON \
        contracts.contract_taskid = tasks.task_id WHERE contracts.contract_complete IS NOT NULL \
        ORDER BY contracts.contract_complete DESC")
        completedContracts = cur.fetchall()
        for contract in completedContracts:
            outputStr += contract[0] + " killed " + contract[1] + " by " + contract[2] + " ("+contract[3].strftime("%a %d %b, %I:%M %p")+")\n"
        sendMsg(chatID, outputStr)
    #elif "text" in data["message"] and data["message"]["text"][0:6] == "/start":


    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def sendMsg(id, msg):
    r = requests.post(
        telegramBotURL+"sendMessage", 
        data = {"chat_id": id, "text": msg, "parse_mode" : "Markdown"})
    print(r.text)