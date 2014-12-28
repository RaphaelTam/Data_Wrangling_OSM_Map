# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 08:23:51 2014

@author: raphaeltam
Use mongo queries to count the number of different cuisines offered by restaurants 
in the area.  Save cuisine types and number of restaurants that offers a particular
cuisine to a file named "updated_cuisine_types". 

"""
import pprint
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

  
def get_cui(db, pipeline):
    result = db.osm.aggregate(pipeline)
    return result
    
def print_to_file (result):
    with open('example_cuisine_types','w') as fo:
        for r in result['result']:
            fo.write('count: '+str(r['count'])+'\t'+'cuisine: '+str(r['_id'])+'\n')

if __name__ == '__main__':
    db = get_db('example')
    pipeline = make_pipeline()
    result = get_cui(db, pipeline)
    print 'Number of distinct cuisines incl. None = {0}'.format(len(result['result']))
    print_to_file(result)
    
    
