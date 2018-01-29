from flask import Flask, render_template, url_for, request, redirect, Response, jsonify
import psycopg2

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

#conn = psycopg2.connect("host=localhost dbname=w user=s password=s")

app = Flask(__name__)
#cache = Client(('https://yenter.io/', 11211))

@app.route("/assassins/")
def index():
    return render_template("login.html")

@app.route("/assassins/<token>")
def displayPage(token):
#    cur = conn.cursor()
#    cur.execute( )
#    data = cur.fetchone( )
    #slice data, add into return statement
    return render_template("info.html", )

@app.route("/assassins/<token>/kill")
def killPage(token):
    # cur = conn.cursor()
    # cur.execute( )
    #set target's status to dead
    #set target's target, task to null
    #set user's new target to that of target's
    return render_template("killconfirmed.html", )

if __name__ == "__main__":
    app.run(debug = True)