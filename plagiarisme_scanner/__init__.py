from .config import *
from flask import Flask, render_template
from .modules.mongo import Mongo
from .modules.scraper import Scraper
from .modules.levenshtein_distance import (
    Text_Cleaner, LevenshteinDistance
)


app = Flask("plagiarisme_scanner")


mongo_db = Mongo(
    auth=mongo_auth, 
    db_name=db_name
)
text_cleaner = Text_Cleaner()
levenshtein_distance = LevenshteinDistance(
    mongo_db=mongo_db, 
    text_cleaner=text_cleaner
)

# inserting result of scrap to database if databse is empty
abstracts = mongo_db.agg(
    coll_name="abstracts", 
    pipline=[
        {'$project': {
            '_id': 1
        }}
    ], 
    output=tuple
)
if len(abstracts) == 0:
    mongo_db.insert(
        coll_name="abstracts", 
        docs=Scraper().fetch(
            preprocessing_callback=text_cleaner.clean
        )
    )


# rendering jinja tempate
def html(template:str, **kwargs):
    return render_template(
        template, 
        app_name=app_name, 
        author=author, 
        **kwargs
    )