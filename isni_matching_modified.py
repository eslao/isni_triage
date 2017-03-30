#!/usr/bin/env python

import requests
import csv
import time
import codecs
from bs4 import BeautifulSoup
import urllib
import re

def parse_isni(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    uri_result_set = soup.find_all('isniuri')
    return uri_result_set

def query_isni(name):
    root = "http://isni.oclc.nl/sru/DB=1.2/"
    params = {
          'query':'pica.nw={0}'.format(name),
          'operation':'searchRetrieve',
          'recordSchema':'isni-b',
          'maximumRecords':1000
          }
    encoded = urllib.urlencode(params)
    search_url = root + '?' + encoded
    return requests.get(search_url)

def get_record_info(uri):
    isni_xml = requests.get(uri.text + '.xml').text
    isni_xml_soup = BeautifulSoup(isni_xml, 'html.parser')
    print "forename: " + isni_xml_soup.forename.text
    print "surname: " + isni_xml_soup.surname.text

def write_csv(filename, content):
    with open(filename, 'wb') as output:
        output.write(codecs.BOM_UTF8)
        writer = csv.writer(output, quoting=csv.QUOTE_ALL,quotechar='"')
        writer.writerows(content)
    print filename, 'has been created'

# Create lists
matches = [['Name', 'ISNI Record URI']]
non_matches = [['Name', 'Original Titles', 'Year of Release', 'Item number']]

# Get unique names
exclude_names = ["Director", "[uncredited]", "[unknown]"]
name_list = []

# Read the file
file = 'sample.csv'
with open(file, 'rb') as name_csv:
        reader = csv.reader(name_csv)
        for row in enumerate(reader):
            name = row[1][3].strip()
            if name not in name_list and name not in exclude_names:
                name_list += [name]
                ### For testing ###
                if len(name_list) > 5:
                    break
                print "Querying ISNI for '{0}'...".format(name)
                isni_response = query_isni(name)
                uri_result_set = parse_isni(isni_response)
                if len(uri_result_set) == 0:
                    print '-> Zero records found\n'
                    non_matches += [[name, row[1][27], row[1][22], row[1][147]]]
                elif len(uri_result_set) > 0:
                    uri_list = []
                    print "-> {0} records found\n".format(len(uri_result_set))
                    for uri in uri_result_set:
                        uri_list += [str(uri)]
                        # get_record_info(uri)
                    matches += [[name, uri_list]]

# Write non-matches to csv
write_csv('non_matches_sample.csv', non_matches)

# Write matches to CSV
write_csv('matches_sample.csv', matches)
