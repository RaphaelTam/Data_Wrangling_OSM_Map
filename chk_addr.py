# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 18:22:37 2014

@author: raphaeltam
"""

import xml.etree.ElementTree as ET
import pprint
import re
"""
Get a feel of the address consistency problem in 2 passes.  The first pass is to 
find  tag keys that have "addr" in all variations.  Use regex to match the addr 
string with any number of before and after characters.
"""
pattern = re.compile('.*addr*\:*\w*')


def find_addr_var(filename):
    addrs = set()
    for _, element in ET.iterparse(filename):    
        if element.tag == 'tag':
            for de in element.iter('tag'):
                if re.match(pattern, de.attrib['k']):
                    addrs.add(de.attrib['k'])
    return addrs


def test():
    variations  = find_addr_var('map.osm')
    print variations

    


if __name__ == "__main__":
    test()