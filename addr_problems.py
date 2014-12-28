# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 00:51:43 2014

@author: raphaeltam
"""
import pprint
import xml.etree.ElementTree as ET

"""
Inspect and manully remove expected keys from the set obtained from chk_addr.py
to get a 'mapping' list.  Expected keys such as 'addr:housenumber' and 'addr:
street' do not go into the mapping list.  The list produced is
the set of keys that should potentially be corrected.

With all the vairations in the mapping list, run through elements to find abnormal
keys and use writedict to save the key-value pairs to a csv file for visual
examination.

"""
def addr_excep(filename):
    data = []
    mapping =['addr:unit', 'addr:full',
    'addr:housenumber:source', 'addr:province', 
    'addr:interpolation', 'addr:housename', 
    'address', 'addr:suite']

    for _, element in ET.iterparse(filename):    
        if element.tag == 'tag':
            for t in element.iter('tag'):
                for odd in mapping:
                    if t.attrib['k'] == odd:
                        data.append(element) 
    return data

def print_to_file(v):
    fieldnames = ['addr:housenumber', 'addr:unit', 'addr:full', 'addr:city', \
    'addr:housenumber:source', 'addr:province', 'addr:postcode', 
    'addr:interpolation', 'addr:housename', 'addr:state', 
    'address', 'addr:county', 'addr:country', 'addr:suite', 'addr:street']

    import csv
    with open('problem_addr.csv', 'w') as fo:
        wr = csv.DictWriter (fo, fieldnames=fieldnames, restval='',\
        extrasaction='ignore')
        wr.writeheader()
        for el in v:
            dic = {}
            for t in el.iter('tag'):
                dic[t.attrib['k']] = t.attrib['v']
            wr.writerow(dic)    

def test():
    v  = addr_excep('map.osm')
    print_to_file(v)


if __name__ == "__main__":
    test()