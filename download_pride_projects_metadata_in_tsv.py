#!/bin/env python2.7
# encoding: utf-8
##################################

# A small script to download in a tsv file all the projects metadata from the EMBL-EBI Pride Archive.

# http://www.ebi.ac.uk/pride/help/archive/access/webservice

# USAGE : python27 download_pride_projects_metadata_in_tsv.py

##################################

import os
import sys
import json
import pprint
# import urllib
# import urllib2

################################### Third-party imports
# pip install requests tablib
import requests
import tablib
###################################

def flatten(seq): # flatten fonction from C:\Python26\Lib\compiler\ast.py
    l = []
    for elt in seq:
        t = type(elt)
        if t is tuple or t is list or t is set:
            for elt2 in flatten(elt):
                l.append(elt2)
        else:
            l.append(elt)
    return l

###################################

dataset = None
page = 0
nb_projects_per_page = 1000
result_is_empty = False
while not result_is_empty:
    query_url = "http://www.ebi.ac.uk:80/pride/ws/archive/project/list?show={}&page={}&order=desc".format(nb_projects_per_page,page)
    print query_url
    results = requests.get(query_url)
    a = results.text.encode('utf-8')
    b = json.loads(a)
    if not b['list']:
        result_is_empty = True
    else:
        subdataset = tablib.Dataset()
        subdataset.dict = b['list']
        if not dataset:
            dataset = subdataset
        else:
            dataset = dataset.stack(subdataset)
        page += 1
        print page, len(dataset)
with open('pride_projects.tsv', 'wb') as f:
    f.write(dataset.tsv)

with open('pride_projects_instruments.tsv', 'wb') as f:
    from itertools import chain
    list_instruments = list(set( list(chain(*dataset['instrumentNames'])) ))
    list_instruments.sort()
    pprint.pprint(list_instruments, stream=f)

    pprint.pprint("", stream=f)

    from collections import Counter
    dict_instruments = Counter( list(chain(*dataset['instrumentNames'])) )
    aa = dict_instruments.items()
    aa.sort(key= lambda x:x[1], reverse=True)
    pprint.pprint(list_instruments, stream=f)

# sys.exit()


dataset = None
pride_projects_dataset = tablib.Dataset().load(open('pride_projects.tsv').read())

nb_accession = len(pride_projects_dataset['accession'])
for i, accession in enumerate(pride_projects_dataset['accession']):
    query_url = "http://www.ebi.ac.uk:80/pride/ws/archive/project/{}".format(accession)
    results = requests.get(query_url)
    a = results.text.encode('utf-8')
    try:
        b = json.loads(a)
    except ValueError: 
        # http://www.ebi.ac.uk/pride/ws/archive/project/PXD001796
        # No JSON object could be decoded
        # a == '<!DOCTYPE html>\n<html>\n<body>\n<meta http-equiv="refresh" content=\'0;URL=http://www.ebi.ac.uk/errors/failure.html\'>\n</body>\n</html>\n'
        continue

    for k,v in b["submitter"].iteritems():
        b["submitter_"+k] = v
    del b["submitter"]
    
    if b["labHeads"]:
        for k,v in b["labHeads"][0].iteritems():
            b["labHeads_"+k] = v
    else:
        for k in ["title", "firstName", "lastName", "email", "affiliation"]:
            b["labHeads_"+k] = ""
    del b["labHeads"]

    # "submitter":{"title":"Dr", "firstName":"Sarah", "lastName":"Hart", "email":"s.r.hart@keele.ac.uk", "affiliation":"Keele University"}
    # "labHeads":[{"title":"Dr", "firstName":"Sarah Ruth", "lastName":"Hart", "email":"s.r.hart@keele.ac.uk", "affiliation":"Keele University"}]

    # del b['sampleProcessingProtocol']
    # del b['dataProcessingProtocol']
    # del b['projectDescription']

    subdataset = tablib.Dataset()
    subdataset.dict = [b]
    if not dataset:
        dataset = subdataset
    else:
        dataset = dataset.stack(subdataset)
    print i+1, '/', nb_accession, accession

with open('pride_projects_details.tsv', 'wb') as f:
    f.write(dataset.tsv)
dataset = None

with open('pride_projects_details_instruments.tsv', 'wb') as f:
    dataset = tablib.Dataset().load(f.read())

    from itertools import chain
    list_instruments = list(set( list(chain(*dataset['instrumentNames'])) ))
    list_instruments.sort()
    pprint.pprint(list_instruments, stream=f)

    pprint.pprint("", stream=f)

    from collections import Counter
    dict_instruments = Counter( list(chain(*dataset['instrumentNames'])) )
    aa = dict_instruments.items()
    aa.sort(key= lambda x:x[1], reverse=True)
    pprint.pprint(list_instruments, stream=f)
