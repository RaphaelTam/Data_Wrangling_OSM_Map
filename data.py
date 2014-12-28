# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 11:45:34 2014

@author: raphaeltam
"""
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

"""
The first task is to wrangle the data and transform the shape of the data
into a model more suited for data analysis. The output is a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

The function 'shape_element' processes the element from xml.etree.ElementTree.iterparse
and returns a dictionary, containing the shaped data for that element.  Shaped data is 
stored in a file, so that mongoimport can be used later on to import the shaped data into 
MongoDB. 

In particular the following things are done:
- I will process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing.  The values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it will be ignored
- if second level tag "k" value starts with "addr:", it will be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", it is processed
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag will be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  will be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

will be turned into
"node_refs": ["305896090", "1719825889"]
"""
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

"""
Process address related information
"""
def p_addr(element):
    addr_dic = {}
    for t in element.iter('tag'):
        if t.attrib.has_key('k'):
            if t.attrib['k']=='addr:housenumber':
                addr_dic['housenumber'] = t.attrib['v']
                continue
            if t.attrib['k'] == 'addr:street':
                addr_dic['street'] = t.attrib['v']
                continue
            if t.attrib['k'] == 'addr:postcode':
                addr_dic['postcode'] = t.attrib['v']
                continue
    return addr_dic

"""
Process amenity related information"
"""    
def p_amenity(element):
    a_d = {}
    for t in element.iter('tag'):
        if t.attrib['k'] == 'amenity':
            a_d['amenity'] = t.attrib['v']
        if t.attrib['k'] == 'name':
            a_d['name'] = t.attrib['v']
        if t.attrib['k'] == 'phone':
            a_d['phone'] = t.attrib['v']
        if t.attrib['k'] == 'cuisine':
            a_d['cuisine'] = t.attrib['v']
        continue
    return a_d     
            
    
#process 'created' information   
def p_created(element):
    cr_dict = {}
    for cr in CREATED:
        cr_dict[cr] = element.attrib[cr]
    return cr_dict

"""
Returns True if the address has a housenumber key
"""
def is_structure(element):
    for e in element.iter('tag'):
        if e.attrib['k'] == 'addr:housenumber':
            return True           
    return False  
    
"""
Retruns true if the node has amenity information
"""    
def has_amenity(element):
    for e in element.iter('tag'):
        if e.attrib['k'] == 'amenity':
            return True
    return False

def p_pos(element):
    return [float(element.attrib['lat']), float(element.attrib['lon'])]  
            
"""
process node elements, pack data into data model
"""          
def p_node(element):
    node = {}
    node['id'] = element.attrib['id']
    node['type'] = 'node'
    if element.attrib.has_key('visible'):
        node['visible'] = 'true'
    node['created'] = p_created(element)
    node['pos'] = p_pos(element)
    if is_structure(element):
        node['address'] = p_addr(element)
    if has_amenity(element):
        for k,v in p_amenity(element).iteritems():
            node[k] = v
    return node
""" 
process way elements and their associated nd tags
"""
def p_nd(element):
    nd_list = []
    for t in element.iter('nd'):
        nd_list.append(t.attrib['ref'])
    return nd_list
    
def p_way(element):
    node = {}
    node['id'] = element.attrib['id']
    node['type'] = 'way'
    node['created'] = p_created(element)
    node['node_refs'] = p_nd(element)
    if is_structure (element):
        node['address'] = p_addr(element)
    
    return node
         
#process node differently from way
def shape_element(element):
    node = {}  
    if element.tag == "node":
        return p_node(element)
    if element.tag == "way":
        return p_way(element)            
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
          
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('map.osm', pretty=False)
 

if __name__ == "__main__":
    test()
    
