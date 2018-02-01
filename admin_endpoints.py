import requests, json
from flask import Blueprint, request, render_template
import psycopg2
from datetime import datetime
from private_vars import conn

adminEndpoints = Blueprint('adminEndpoints', __name__, template_folder='templates')

@adminEndpoints.route("/assassins/admin")
def index():
    return render_template("admin-login.html")