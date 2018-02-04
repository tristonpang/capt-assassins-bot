import requests, json
from flask import Blueprint, request
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, connStr

# from flask_cache import Cache

ids = set()

teleBot = Blueprint('teleBot', __name__, template_folder='templates')

# cache = SimpleCache()
# cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/'})

@teleBot.route('/assassins/telegram/update/', methods = ["POST"])
def telegramUpdate():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()
    data = request.get_json()
    chatID = data["message"]["chat"]["id"]
    print(data)
    if chatID not in ids:
        ids.add(chatID)
    if "text" in data["message"] and data["message"]["text"][0:7] == "/status":
        # Send update
        print("Received status update request")
        # Fetch status
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
        cur.execute("SELECT assassin.user_nickname, target.user_nickname, \
        contracts.contract_complete FROM contracts INNER JOIN users AS assassin ON \
        contracts.contract_assid = assassin.user_id INNER JOIN users AS target ON \
        contracts.contract_targetid = target.user_id WHERE contracts.contract_complete IS NOT NULL \
        ORDER BY contracts.contract_complete DESC")
        completedContracts = cur.fetchall()
        for contract in completedContracts:
            outputStr += contract[0] + " killed " + contract[1] + " ("+contract[3].strftime("%a %d %b, %I:%M %p")+")\n"
        sendMsg(chatID, outputStr)
    elif "text" in data["message"] and data["message"]["text"][0:6] == "/start":
        user_hash = data["message"]["text"][7:]
        #retrieve associated user_id, store tele_chat_id
        cur.execute("SELECT user_id FROM tele_ids WHERE tele_hash = %s", (user_hash,))
        user_id = cur.fetchone()[0]
        cur.execute("UPDATE users SET user_telegram = %s WHERE user_id = %s", (chatID, user_id,))
        cur.execute("DELETE FROM tele_ids WHERE user_id = %s", (user_id,))
    
    cur.close()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def sendMsg(id, msg):
    r = requests.post(
        telegramBotURL+"sendMessage", 
        data = {"chat_id": id, "text": msg, "parse_mode" : "Markdown"})
    print(r.text)