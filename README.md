# capt-assassins-bot

## Introduction

This project is a Flask-based Python project that facilitates keeping track of an Assassins game. 

The Python scripts assume a VPS with a domain name tagged to it. A Telegram bot should also be created, and configured to [receive webhooks](https://core.telegram.org/bots/api#setwebhook). More information on webhooks [can be found here](https://core.telegram.org/bots/webhooks). The code can also probably be reconfigured for long-polling if need be. 

## Files

1. `wsgi.py` -- Provides an entry point for running the app via WSGI, which provides faster speeds than just using Flask's inbuilt development server. [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html) is a good alternative. 
2. `assassins_web.py` -- Called by `wsgi.py`, and is the main entry point for the app. 
3. `admin_endpoints.py` provides a Web UI for the admins to access information and confirm keys.
4. `telegram.py` handles all Telegram-related APIs. 
5. `users_endpoints.py` provides a Web UI for players to interact with.

## Getting Started

1. You will need a Postgresql database set up. < Include the set up instructions here>
2. Install the required Python libraries:
  
  ```bash
  $ pip install flask requests psycopg2 uwsgi
  ```
  
3. Clone the directory:
  
  ```bash
  $ git clone https://github.com/tristonpang/capt-assassins-bot
  ```
  
4. `cd` in:
  
  ```bash
  $ cd capt-assassins-bot
  ```
  
5. Start up a uWSGI server:
  
  ```bash
  $ uwsgi --http :5000 --wsgi-file wsgi.py
  ```
