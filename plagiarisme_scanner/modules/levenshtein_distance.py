import string
import typing as t
from .mongo import Mongo
import Levenshtein as lev
from .scraper import Scraper
# from nltk.corpus import stopwords
# import nltk
# nltk.download()


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

