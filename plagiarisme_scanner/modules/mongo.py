import typing as t
from bson import ObjectId
from pymongo import MongoClient


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