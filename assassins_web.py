from flask import Flask
from telegram import teleBot
from users_endpoints import usersEndpoints
from admin_endpoints import adminEndpoints


# cache = SimpleCache()

# conn = psycopg2.connect("host=localhost dbname=assassins user=assassins password=captslock")

app = Flask(__name__)
app.register_blueprint(usersEndpoints)
app.register_blueprint(adminEndpoints)
app.register_blueprint(teleBot)

if __name__ == "__main__":
	app.run(debug = True)