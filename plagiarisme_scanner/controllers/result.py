from plagiarisme_scanner import app, html, mongo_db


@app.route("/result")
def result():
    scanning = False
    percentage = None
    result_available = False

    status = mongo_db.agg(
        coll_name="status", 
        pipline=[{'$project': {'scanning': '$scanning', '_id': 0}}], 
        output=tuple
    )
    if len(status) > 0:
        if status[0]['scanning']:
            scanning = True

    result = mongo_db.agg(
        coll_name="results", 
        pipline=[
            {'$sort': {'_id': -1}}, 
            {'$limit': 1}, 
            {'$project': {'percentage': '$percentage', '_id': 0}}
        ], 
        output=tuple
    )
    if len(result) > 0:
        result_available = True
        percentage = result[0]['percentage']


    return html(
        'page/result.html', 
        page='result', 
        percentage=percentage, 
        scanning=scanning, 
        result_available=result_available
    )
