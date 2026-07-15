from flask import Flask, request, jsonify
import json
import os
import threading
import time

app = Flask(__name__)

DB="registry.json"
LOCK=threading.Lock()

if not os.path.exists(DB):
    with open(DB,"w") as f:
        json.dump({},f)


def load():
    with open(DB) as f:
        return json.load(f)


def save(data):
    with open(DB,"w") as f:
        json.dump(data,f,indent=4)


@app.route("/register",methods=["POST"])
def register():

    data=request.json

    with LOCK:

        db=load()

        db[data["flight"]]={
            "pilot":data["pilot"],
            "telemetry":data["telemetry"],
            "stream":data["stream"],
            "heartbeat":time.time()
        }

        save(db)

    return {"status":"registered"}


@app.route("/heartbeat",methods=["POST"])
def heartbeat():

    data=request.json

    with LOCK:

        db=load()

        if data["flight"] in db:

            db[data["flight"]]["heartbeat"]=time.time()

            save(db)

    return {"status":"ok"}


@app.route("/unregister",methods=["POST"])
def unregister():

    data=request.json

    with LOCK:

        db=load()

        db.pop(data["flight"],None)

        save(db)

    return {"status":"removed"}


@app.route("/fleet")
def fleet():

    with LOCK:

        db=load()

        now=time.time()

        remove=[]

        for k,v in db.items():

            if now-v["heartbeat"]>30:

                remove.append(k)

        for k in remove:

            del db[k]

        save(db)

        return jsonify(db)


@app.route("/")
def home():

    return "ACHUK Fleet Registry Running"


if __name__=="__main__":

    app.run(host="0.0.0.0",port=10000)
