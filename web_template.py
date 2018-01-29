from flask import Flask, render_template, url_for, request, redirect, Response, jsonify
import psycopg2

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

conn = psycopg2.connect("host=posql.yenter.io dbname=w user=s password=s")

app = Flask(__name__)
#cache = Client(('https://yenter.io/', 11211))

@app.route("/wayfarer/fetchStatus/<task_id>")
def fetchStatus(task_id):
    task = pullResults.AsyncResult(task_id)
    if task.state == 'PROGRESS':
        info = task.info
    else:
        info = str(task.info)
    response = {
        'state': task.state,
        'info': info, 
        'status': task.status
    }
    return jsonify(response)

@app.route("/wayfarer/")
def index():
    countries = []
    return render_template("form.html", cities = placeNames_a)

@app.route("/wayfarer/search/<searchString>")
def searchString(searchString):
    MAX_RESULTS = 5
    priorityResults = []
    normalResults = []
    cleaned = regex.sub("", searchString).lower()

    for place in placeNames_a:
        if cleaned in place["cleaned"]:
            if cleaned == place["cleaned"][0:len(cleaned)]:
                # Priority
                priorityResults.append(place)
                if (len(priorityResults) >= MAX_RESULTS):
                    break
            elif len(priorityResults) + len(normalResults) < MAX_RESULTS:
                normalResults.append(place)
    
    if (len(priorityResults) < MAX_RESULTS):
        for place in placeNames_p:
            if cleaned in place["cleaned"]:
                if cleaned == place["cleaned"][0:len(cleaned)]:
                    # Priority
                    priorityResults.append(place)
                    if (len(priorityResults) >= MAX_RESULTS):
                        break
                elif len(priorityResults) + len(normalResults) < MAX_RESULTS:
                    normalResults.append(place)

    return '{"status": "done", "result": '+json.dumps((priorityResults + normalResults)[0:min(MAX_RESULTS, len(priorityResults) + len(normalResults))])+'}'

@app.route("/wayfarer/results/<countryRaw>/<placeRaw>/")
def results(placeRaw, countryRaw):
    # raw: from the URL
    # L: lowercase, with spaces replaced by _
    # Pretty: Title case, with spaces
    placeL = lowerName(placeRaw)
    countryL = lowerName(countryRaw)
    placePretty = prettyName(placeL)
    countryPretty = prettyName(countryL)
    
    placeFilename = placesCache(placeL, countryL)
    foodFilename = foodCache(placeL, countryL)
    
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO history (ip, country, place, timestamp) VALUES (%s, %s, %s, now())", 
            (request.headers['X-Forwarded-For'], countryRaw, placeRaw)
        )
        conn.commit()
    except psycopg2.Error as e:
        print(e)
        print(e.pgerror)
    except:
        pass
    cur.close()

        return render_template("results.html", city = placePretty, \
                            country = countryPretty, places = placesFound, \
                            groups = list(groups), numGroups = len(groups), \
                            food = foodResult, foodGroups = foodGroups, \
                            accoms = [], custom = False)

@app.route("/wayfarer/itinerary/create/", methods=['POST'])
def createItinerary():
    # Receive as POST
    content = request.get_json()
    hash = secrets.token_urlsafe(18)[0:16]
    # print(json.dumps(content["itinerary"]))
    itinerary = json.dumps(content["itinerary"])
    accoms = json.dumps(content["accoms"])
    # return(json.dumps({'status': 'ok', 'hash': 'hash'}))
    # Also check if the hash exists

    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO itineraries (ip, country, place, timestamp, hash, days, places, accom) VALUES (%s, %s, %s, now(), %s, %s, %s, %s)", 
            ("", content["country"], content["place"], hash, content["days"], itinerary, accoms)
        )
        conn.commit()
    except psycopg2.Error as e:
        print(e.pgerror)
        return json.dumps({'status': 'error', 'message': e.pgerror})
    except Exception as error:
        print(error)
        return json.dumps({'status': 'error', 'message': error})
    cur.close()

    return json.dumps({"status": "ok", "hash": hash})


if __name__ == "__main__":
    app.run(debug = True)