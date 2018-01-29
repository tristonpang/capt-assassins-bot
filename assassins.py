import requests

url = "https://api.telegram.org/bot454094709:AAHlLv5OfquuiTfZ7aGMG9l7-5uhJh_VZxU/"

'''Takes in url(request) and gets response data. Returns in json format'''
def get_updates_json(request):
    params = {"timeout": 100, "offset": None} #timeout if no recent updates, offset to indicate a certain update is already seen
    response = requests.get(request + "getUpdates", data=params)
    return response.json()


'''Takes in json data and returns the
last entry in the result collection (last update)'''
def last_update(data):
    return data["result"][-1]

'''Takes in an update and returns the chat id'''
def get_chat_id(update):
    chat_id = update["message"]["chat"]["id"]
    return chat_id

'''Makes bot send a message by appending query to end of url with
respective parameters'''
def send_msg(chat, text):
    params = {"chat_id": chat, "text": text}
    #equivalent to <url>/sendMessage?chat_id=<id>&text=<msg> (chaining params)
    response = requests.post(url + "sendMessage", data=params)
    return response

def process_request(update):
    chat_id = update["message"]["chat"]["id"]
    if update["message"]["text"] == "/kill":
        send_msg(chat_id, "Kill command received")
    else:
        send_msg(chat_id, "Default response")

chat_id = get_chat_id(last_update(get_updates_json(url)))

send_msg(chat_id, "Hello world! Assassin's Bot script started!")

def main():
    last_seen_update_id = last_update(get_updates_json(url))["update_id"]
    while True:
        poll_id = last_update(get_updates_json(url))["update_id"]
        if last_seen_update_id != poll_id:
            updates = get_updates_json(url)["result"]
            updates = list(filter(lambda x:x["update_id"] > last_seen_update_id, updates))
            
            for update in updates:
                process_request(update)

            last_seen_update_id = poll_id

            
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
