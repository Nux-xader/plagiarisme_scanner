from plagiarisme_scanner import app, html, mongo_db


def parse_unit(num:int) -> str:
    if num >= 1000:
        num = num/1000
        
        if num >= 1000:
            num = num/1000
            num = float("{:.2f}".format(num))

            if int(num) == num:
                num = int(num)
            num = f"{num}M"
        else:
            num = float("{:.2f}".format(num))
            if int(num) == num:
                num = int(num)
            num = f"{num}K"
    
    return str(num)


@app.route("/")
def dashboard():
    total_abstracts = mongo_db.agg(
        coll_name="abstracts", 
        pipline=[{'$group': {'_id': None, 'total': {'$sum': 1}}}], 
        output=tuple
    )
    if len(total_abstracts) < 1: total_abstracts = 0
    else: total_abstracts = total_abstracts[0]['total']
    total_abstracts = parse_unit(total_abstracts)

    scanned_data = mongo_db.agg(
        coll_name="results", 
        pipline=[
            {'$facet': {
                'data': [
                    {'$sort': {'_id': 1}}, 
                    {'$project': {
                        '_id': 0, 
                        'percentage': '$percentage', 
                        'scanning_time': {
                            '$dateToString': {
                                'date': {'$toDate': {
                                    '$multiply': ['$scanning_time', 1000]
                                }}
                            }
                        }
                    }}
                ]
            }}, 
            {'$project': {
                '_id': 0, 
                'percentages': '$data.percentage', 
                'graph': {'$slice': ["$data", 15]}
            }}
        ], 
        output=tuple
    )

    if len(scanned_data[0]['graph']) == 0:
        graph = []
        scanned = []
        avg_plagiarism = "-"
    else:
        graph = scanned_data[0]['graph']
        scanned = scanned_data[0]['percentages']

        avg_plagiarism = float("{:.2f}".format(sum(scanned)/len(scanned)))
        if int(avg_plagiarism) == avg_plagiarism:
            avg_plagiarism = int(avg_plagiarism)
        avg_plagiarism = f"{avg_plagiarism}%"

    return html(
        'page/dashboard.html', 
        page='dashboard', 
        graph=graph, 
        total_abstracts=total_abstracts, 
        total_scanned=parse_unit(len(scanned)), 
        avg_plagiarism=avg_plagiarism

    )