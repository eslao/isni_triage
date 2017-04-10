#!/usr/bin/env python

import requests
import csv, time, sys, re
import codecs
from bs4 import BeautifulSoup
import urllib

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
matches = [['Name', 'Number of Matching Records', 'ISNI Record URIs']]
non_matches = [['Name', 'Original Titles', 'Year of Release', 'Item number']]

# Get unique names
exclude_names = ["Director", "[uncredited]", "[unknown]"]
name_list = []

# Input filename
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    print "Please provide a CSV file.\n"

# Clean up any null bytes in csv
fi = open(input_file, 'rb')
data = fi.read()
fi.close()
clean_file = 'clean_' + input_file
fo = open(clean_file, 'wb')
fo.write(data.replace('\x00', ''))
fo.close()

# Read the file
with open(clean_file, 'rb') as name_csv:
    reader = csv.reader(name_csv)
    for row in enumerate(reader):
        name = row[1][3].strip()
        if name not in name_list and name not in exclude_names:
            name_list += [name]
            ### For testing ###
            # if len(name_list) > 15:
            #     break
            print "\nQuerying ISNI for '{0}'...".format(name)
            isni_response = query_isni(name)
            uri_result_set = parse_isni(isni_response)
            if len(uri_result_set) == 0:
                print '-> Zero records found'
                non_matches += [[name, row[1][27], row[1][22], row[1][147]]]
            elif len(uri_result_set) > 0:
                uri_list = []
                print "-> {0} records found".format(len(uri_result_set))
                for idx, uri in enumerate(uri_result_set):
                    # Cap the number of URIs output at 5
                    if idx > 4:
                        print "-> Too many records! Outputting the first 5 URIs; search for the rest manually.\n"
                        uri_list += ["..."]
                        break
                    uri_list += [str(uri)]
                    # get_record_info(uri)
                matches += [[name, len(uri_result_set), uri_list]]

# Write non-matches to csv
write_csv("non-matches_" + input_file, non_matches)

# Write matches to CSV
write_csv("matches_" + input_file, matches)
