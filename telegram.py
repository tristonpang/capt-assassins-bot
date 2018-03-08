import requests, json
from flask import Blueprint, request
import psycopg2
from datetime import datetime
from private_vars import telegramBotURL, connStr

teleBot = Blueprint('teleBot', __name__, template_folder='templates')

@teleBot.route('/assassins/telegram/update/', methods = ["POST"])
def telegramUpdate():
    conn = psycopg2.connect(connStr)
    conn.autocommit = True
    cur = conn.cursor()

    data = request.get_json()
    print(data)
    if "message" in data:
        chatID = data["message"]["chat"]["id"]
        if "text" in data["message"] and data["message"]["text"][0:7] == "/status":
            # Send update
            print("Received status update request")
            # Fetch status
            outputStr = fetchStatus(cur)
            sendMsg(chatID, outputStr)
        elif "text" in data["message"] and data["message"]["text"][0:6] == "/start":
            user_hash = data["message"]["text"][7:]
            #retrieve associated user_id, store tele_chat_id
            
            cur.execute("SELECT user_id FROM tele_ids WHERE tele_hash = %s", (user_hash,))
            data = cur.fetchone()
            if data is not None:
                user_id = data[0]
                cur.execute("UPDATE users SET user_telegram = %s WHERE user_id = %s", (chatID, user_id,))
                cur.execute("DELETE FROM tele_ids WHERE user_id = %s", (user_id,))
    cur.close()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def sendMsg(id, msg):
    r = requests.post(
        telegramBotURL+"sendMessage", 
        data = {"chat_id": id, "text": msg, "parse_mode" : "Markdown"})
    print(r.text)

def sendConfirmMsg(id, msg):
    keyboard = {
        "inline_keyboard": [
            [{
                "text": "Accept", 
                "callback_data": json.dumps({"decision": "accept", "contractID": 3})
            }], 
            [{
                "text": "Reject", 
                "callback_data": json.dumps({"decision": "reject", "contractID": 3})
            }]
        ]
    }
    r = requests.post(telegramBotURL+"sendMessage", data = {
        "chat_id": id, 
        "text": msg, 
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    })
    print(r.text)

@teleBot.route("/testing/")
def sendTestMsg():
    sendConfirmMsg(167223959, "An assassination attempt has been logged.")
    sendConfirmMsg(398049566, "An assassination attempt has been logged.")

def fetchStatus(cur):
    outputStr = "*Completed Contracts*\n"
    cur.execute("SELECT assassin.user_nickname, target.user_nickname, \
    contracts.contract_complete FROM contracts INNER JOIN users AS assassin ON \
    contracts.contract_assid = assassin.user_id INNER JOIN users AS target ON \
    contracts.contract_targetid = target.user_id WHERE contracts.contract_complete IS NOT NULL \
    ORDER BY contracts.contract_complete DESC")
    completedContracts = cur.fetchall()
    for contract in completedContracts:
        outputStr += "`"+contract[0] + "` killed `" + contract[1] + "` ("+contract[2].strftime("%a %d %b, %I:%M %p")+")\n"
    
    cur.execute("SELECT users.user_nickname, users.user_alive, count(case when contracts.contract_complete > '2018-03-07 20:30:00' then 2 else null end) + count(contracts.contract_complete) points FROM users LEFT JOIN contracts ON users.user_id = contracts.contract_assid GROUP BY users.user_id ORDER BY users.user_alive DESC, points DESC, users.user_nickname")
    users = cur.fetchall()
    outputStr += "\n*Alive Players*\n"
    alive = True
    for user in users:
        kills = " ("
        if user[2] != 1:
            kills += str(user[2])+" points"
        else:
            kills += "1 point"
        kills += ")"
        # userData = "`" + user[0] + "` ("
        # if user[2] != 1:
        #     userData += str(user[2])+" kills"
        # else:
        #     userData += "1 kill"
        # userData += ")"
        if user[1]:
            outputStr += user[0].replace("_", "\_") + kills + "\n"
        else:
            if alive:
                alive = False
                outputStr += "\n*Dead Players*\n"
            outputStr += user[0].replace("_", "\_") + kills + "\n"
    print(outputStr)
    return outputStr
