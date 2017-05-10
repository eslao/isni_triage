identifiers = ['0000 0000 7328 0710', '0000 0000 6648 4467', '0000 0000 4977 6257']
uris = []
for isni_number in identifiers:
    uris += ['http://www.isni.org/isni/' + isni_number.replace(' ', '')]
print uris

g2 = rdflib.Graph()

for uri in uris:
    print uri
    g1 = rdflib.Graph()
    rdfurl = uri + '.rdf'
    g1.parse(rdfurl, format='xml')
    for s, p, o in g1:
        g2.add( (URIRef(uri), p, o) )
        
print( g2.serialize(format='n3') )
