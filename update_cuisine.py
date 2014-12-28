# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 19:59:03 2014

@author: raphaeltam
Minimal cleaning of cuisine types: convert all to lower case and correct obvious 
inconsistencies due to spelling errors.
"""
import re
mapping = ['Mexican','Pizza','Thai','Pakistani','Brasilian','Chinese']
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    pipeline = [{'$match':{'amenity':'restaurant'}},
              {'$group':{'_id':'$cuisine','count':{'$sum':1}}}
                ]
    return pipeline   

def cor_cap(cap, db):
    db.map.osm.update({'cuisine':cap},
                      {"$set": {'cuisine':cap.lower()}},multi=True
                      )
    return
    
def cor_oddballs(db):
    db.map.osm.update({'cuisine':'Comfort_Food'},
                      {'$set': {'cuisine':'comfort_food'}}
                      )
    db.map.osm.update({'cuisine':'thai:lao'},
                      {'$set': {'cuisine':'thai;lao'}}
                      )
    db.map.osm.update({'cuisine':'california'},
                      {'$set': {'cuisine':'californian'}}
                      )
    return
        
if __name__ == '__main__':
    db = get_db('example')
    for cuisine in mapping:
        cor_cap(cuisine,db)
    cor_oddballs(db)
    