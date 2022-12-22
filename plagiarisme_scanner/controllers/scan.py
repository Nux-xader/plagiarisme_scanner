import time
from flask import request
from bson import ObjectId
from datetime import datetime
from threading import Thread
from plagiarisme_scanner import app, html, mongo_db, levenshtein_distance


def percentage(text:str):
    scanning_id = ObjectId()
    scanning_time = datetime.now().timestamp()

    mongo_db.insert(
        coll_name="status", 
        docs={"_id": scanning_id, "scanning": True}
    )
    time.sleep(5)
    result = levenshtein_distance.plagiarism_percentage(text=text)
    mongo_db.del_one(
        coll_name="status", 
        filters={"_id": scanning_id}
    )
    mongo_db.insert(
        coll_name="results", 
        docs={
            "percentage": result, 
            "scanning_time": scanning_time
        }
    )


def response(success:bool=True, msg:str="", scanning:bool=True):
    return html(
        'page/scan.html', 
        page='scan', 
        success=success, 
        scanning=scanning, 
        msg=msg
    )

@app.route("/scan", methods=["GET", "POST"])
def scan():
    msg = ""
    success = True
    scanning = False

    status = mongo_db.agg(
        coll_name="status", 
        pipline=[{'$project': {'scanning': '$scanning', '_id': 0}}], 
        output=tuple
    )
    if len(status) > 0:
        if status[0]['scanning']:
            scanning = True
            msg = "Masih ada text yang sedang di scan, tunggu beberapa saat"

    if request.method == "POST":
        if scanning: return response(success=False, scanning=scanning, msg="Scanning gagal, karena masih ada text yang sedang di scan")
        Thread(target=percentage, args=(request.form["text"], )).start()
        scanning = True
        msg = "Text sedang di scan"
    
    return response(success=success, msg=msg, scanning=scanning)