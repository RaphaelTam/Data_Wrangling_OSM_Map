# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 10:32:50 2014

@author: raphaeltam
Audit the value of "addr:stree" key.  Extracts address typs such as street
road, avenue etc. to identify variations that can be corrected with a 
map produced manually.
'expected' is the list of accepted street_types and "mapping" maps variations
to their expected forms.
Minimal processing is done to correct a small number of steet_type variations, but
much more needs to be done.
Street types are written to a file for further examination.  A correction strategy
can be developed to improve data consistency and uniformity.
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "map.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# mapping the variations to be fixed with update_name
mapping = { "St": "Street",
            "St.": "Street",
            "ST": "Street",
            "Ave": "Avenue",
            "Ave.":"Avenue",
            "AVE" :"Avenue",
            "Rd":"Road",
            "Rd.": "Road",
            "RD.": "Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_name(name, mapping):
    m = street_type_re.search(name)
    bad_name = m.group()
    if bad_name in mapping.keys():
        name = name.replace(bad_name, mapping[bad_name])
        
    return name

"""
Audit stret_types for variations in the vaue of "addr:street".
Minimal corretions done with update_name 
Write street_type variations to a file for further examination. The objective
is to develop a strategy on what to clean and how.
"""
def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
    with open('st_types', 'w') as fo:
        for st in st_types.keys():
            fo.write (st+'\n')
    


if __name__ == '__main__':
    test()