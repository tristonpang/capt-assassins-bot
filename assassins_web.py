from flask import Flask
from telegram import teleBot
from users_endpoints import usersEndpoints

app = Flask(__name__)
app.register_blueprint(usersEndpoints)
app.register_blueprint(teleBot)

if __name__ == "__main__":
    app.run(debug = True)