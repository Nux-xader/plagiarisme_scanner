import string
import typing as t
import Levenshtein as lev
from bson import ObjectId
from scraper import Scraper
from pymongo import MongoClient
# from nltk.corpus import stopwords
# import nltk
# nltk.download()



class Mongo:
    def __init__(self, auth:str, db_name:str) -> None:
        self.auth = auth
        self.db_name = db_name
        self.client = MongoClient(self.auth)
        self.db = self.client[self.db_name]
    
    def insert(
        self, 
        coll_name:str, 
        docs:t.Union[dict, list, tuple]
    ) -> t.Union[ObjectId, t.List[ObjectId]]:
    
        if isinstance(docs, dict):
            return self.db[coll_name].insert_one(docs).inserted_id
        elif isinstance(docs, list) or isinstance(docs, tuple):
            return self.db[coll_name].insert_many(docs).inserted_ids
    
    def agg(self, coll_name:str, pipline:list=[], output:t.Optional[t.Union[tuple, list]]=None):
        result = self.db[coll_name].aggregate(pipline)
        if output is None: return result 
        return output(result)
    
    def update(
        self, 
        coll_name:str, 
        filters:dict, 
        update:dict, 
        project:dict=None, 
        many:bool=False
    ) -> t.Union[dict, int]:
        if many: 
            return self.db[coll_name].update_many(
                filter=filters, update=update
            ).modified_count
        
        return self.db[coll_name].find_one_and_update(
            filter=filters, 
            update=update, 
            projection=project
        )
    
    def del_one(self, coll_name:str, filters:dict) -> int:
        return self.db[coll_name].delete_one(filters).deleted_count

    def del_many(self, coll_name:str, filters:dict) -> int:
        return self.db[coll_name].delete_many(filters).deleted_count


class Text_Cleaner:
    def __init__(self) -> None:
        # the strng of punctuations
        self.punctuations = string.punctuation+'“'
        # This data fetched from NLTK stop_word database
        self.stop_words = (
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
            'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
            "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
            'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 
            'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
            'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
            'through', 'during', 'before', 'after', 'above', 'below', 'to', 
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
            'can', 'will', 'just', 'don', "don't", 'should', "should've", 
            'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 
            "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', 
            "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', 
            "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', 
            "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', 
            "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', 
            "won't", 'wouldn', "wouldn't"
        )

    def remove_punctuations(self, text:str):
        '''
        Removing punctuations from the text
        '''
        return ''.join(tuple(filter(lambda x: x not in self.punctuations, text)))
    
    def remove_stopwords(self, text:str):
        '''
        removing stop words on text
        '''
        return ' '.join(tuple(filter(lambda x: x.lower() not in self.stop_words, text.split())))

    def clean(self, text):
        '''
        This function will clean the text being passed by removing specific line feed characters
        like '\n', '\r', and '\'
        '''
        
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\'', '')
        return self.remove_stopwords(self.remove_punctuations(text)).lower()


class LevenshteinDistance:
    def __init__(self, mongo_db:Mongo, text_cleaner:Text_Cleaner) -> None:
        self.lev = lev
        self.mongo_db = mongo_db
        self.text_cleaner = text_cleaner
    
    def add_abstract(self, text:str, coll_name:str="abstracts"):
        self.mongo_db.insert(
            coll_name=coll_name, 
            docs={'text': text}
        )
    
    def plagiarism_percentage(self, text:str, add_db:bool=True):
        text = self.text_cleaner.clean(text)
        cursor = self.mongo_db.agg(
            coll_name="abstracts", 
            pipline=[
                {'$sort': {
                    '_id': -1
                }}, 
                {'$project': {
                    '_id': 0, 
                    'text': '$text'
                }}
            ]
        )
        max_percentage_plagiarism = 0
        for abstract_db in cursor:
            percentage = lev.ratio(abstract_db['text'], text)
            if percentage > max_percentage_plagiarism:
                max_percentage_plagiarism = percentage
            if abstract_db == text: add_db = False

            # abstract_db = abstract_db['text']
            # dist = self.lev.distance(abstract_db, text)
            # if dist == 0 or abstract_db == text: add_db = False
            # if dist \
            #     <= max(len(text), len(abstract_db))*0.4:
            #     return True
        
        if add_db: self.add_abstract(text=text)
        result = float("{:.2f}".format(max_percentage_plagiarism*100))
        if result == int(result): result = int(result)
        return result




mongo_db = Mongo(
    auth="mongodb://localhost:27017", 
    db_name="learn_mongo"
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



##################
###  TESTING  ####
##################
if __name__ == "__main__":
    while True:
        try:
            text_path = input("Enter abstract text path file (.txt): ")
            text = open(text_path, "r").read()
            break
        except:
            print(f"File {text_path} not found")


    print(levenshtein_distance.plagiarism_percentage(text=text))

