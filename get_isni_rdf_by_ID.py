import requests
import csv, time, sys, re
import codecs
from bs4 import BeautifulSoup
import urllib
import rdflib

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF

identifiers = [] #insert list of ISNI numbers with or without spaces here
#identifiers = ['0000 0000 7328 0710', '0000 0001 2103 7046', '0000 0000 6648 4467', '0000 0000 4977 6257']
uris = []
for isni_number in identifiers:
    uris += ['http://www.isni.org/isni/' + isni_number.replace(' ', '')]
#print uris

rdf_urls = []

for uri in uris:
    rdf_content = requests.get(uri + '.rdf')
    if rdf_content.text != '':
        rdf_urls += [uri + '.rdf']
    else:
        print uri + ' is a problem'
        
#print rdf_urls

g2 = rdflib.Graph()

for rdf_url in rdf_urls:
    #print rdf_url
    g1 = rdflib.Graph()
    g1.parse(rdf_url, format='xml')
    for s, p, o in g1:
        g2.add( (URIRef(rdf_url), p, o) )
        
print( g2.serialize(format='ttl') )
