import requests
import csv
import time
import codecs
from bs4 import BeautifulSoup

def getTextOrPlaceholder(tag,placeholderText):
    if tag:
        return tag.text
    else:
        return placeholderText
    
def parseIsniResult(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    result_row = [name]
    for uri in soup.find_all('isniuri'):
        isni_text = requests.get(uri.text + '.xml').text
        isni_text_soup = BeautifulSoup(isni_text, 'html.parser')
        time.sleep(1)
        forename = getTextOrPlaceholder(isni_text_soup.forename, 'no forename')
        surname = getTextOrPlaceholder(isni_text_soup.surname, 'no surname')
        result_row += [surname + ', ' + forename, uri.text ]
    return result_row

	
# Get unique names
	
name_list = []
file = 'sample.csv'
with open(file, 'rb') as name_csv:
        reader = csv.reader(name_csv)
        for row in enumerate(reader):
            # print row[1][3]
            name = row[1][3]
            #print row[1][19]
            if name not in name_list:
                name_list += [name]
                

# Query ISNI API				
				
result_table = []
no_matches = []
matches = []

for name in name_list:
    print name
    url = 'http://isni.oclc.nl/sru/?query=pica.nw+%3D+"' + name + '"&operation=searchRetrieve&recordSchema=isni-b'
    response = requests.get(url)
    time.sleep(1)
    if '<srw:numberOfRecords>0</srw:numberOfRecords>' in response.text:
        print 'zero results'
        result_table += [[name, 'no matches']]
        no_matches += [name]
    else: 
        print 'parsing response'
        result_table += [parseIsniResult(response)]
        matches += [parseIsniResult(response)]


# Write unmatched names to CSV		
		
no_matches_titles = [['Name', 'Titles']]
file = 'sample.csv'

for name in no_matches:
    #record_list = []
    title_list = []
    with open(file, 'rb') as name_csv:
        reader = csv.reader(name_csv)
        for row in enumerate(reader):
            #print row[0]
            #print row[1][3]
            reader_name = row[1][3]    
            if name.lower() in reader_name.lower():
                #record_list += [row[1][147]]
                title_list += [row[1][27] + ' (' + row[1][22] + ', item no.' + row[1][147] + ')']
    #if len(record_list) > 0:
    #    print name 
    #    print record_list
    #    print title_list
    title_list.insert(0, name)
    no_matches_titles += [title_list]

print no_matches_titles

csv_file = 'no_matches_sample.csv'
csv_data = no_matches_titles

with open(csv_file, 'wb') as output:
    output.write(codecs.BOM_UTF8)
    writer = csv.writer(output, quoting=csv.QUOTE_ALL,quotechar='"')
    writer.writerows(csv_data)
print csv_file, 'has been created'


# TO DO: write matches to separate CSV
