#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from os import path
import requests
import xml.etree.ElementTree as ET
from time import sleep


class Data:
    BOOKDIR = '/home/nas/books'
    FORMATS = ['.epub', '.mobi', '.azw3', '.azw']
    APIKEY = ''
    APIURL = 'https://www.goodreads.com/search.xml'
    TIMEOUT = 15

    def fileindex(self):
        filestocheck = []
        #Find all files in the book directory recursively
        rawls = subprocess.check_output(['find', self.BOOKDIR, '-type', 'f']).splitlines()
        for line in rawls:
            data = {}
            filepath = path.normpath(line)
            #Get filename without the path
            filename = path.split(filepath)[1]
            #Check if file extension is allowed
            if path.splitext(filename)[1] not in self.FORMATS:
                continue
            #Useful data for later
            data['filepath'] = filepath
            data['filename'] = filename
            data['filenoext'] = path.splitext(filename)[0]
            filestocheck.append(data)
        return filestocheck

    def get_info_from_api(self, filestocheck):
        parsefail = 0 #For debugging
        apicalls = 0 #For debugging
        for data in filestocheck:
            doapicall = True
            for item in self.itemdata:
                dupcheck = []
                for f in item['filepath']:
                    if f in dupcheck:
                        item['filepath'].remove(f)
                    else:
                        dupcheck.append(f)
                    if data['filepath'] == f:
                        doapicall = False
                        break
                if not doapicall:
                    break
            if doapicall:
                #Call to the API search function
                try:
                    #Get rid of some unnecessary chars in the search string
                    q = data['filenoext'].replace(',', ' ')
                    q = q.replace('-', ' ')
                    q = ' '.join(q.split())
                    payload = {'key':self.APIKEY, 'q':q}
                    #Count the API calls
                    apicalls += 1
                    #Be nice and don't hammer the API to oblivion
                    sleep(3)
                    #Send the API request
                    r = requests.get(self.APIURL, params=payload, timeout=self.TIMEOUT)
                    print '[%s] Making an API call to Goodreads' % (apicalls)
                    print '  API call: %s' % (r.url)
                    apidata = r.text
                except:
                    print 'Goodreads took longer than %s seconds to respond, aborting remaining API calls' % (TIMEOUT)
                    break
                #Parsing and getting the API data we want
                try:
                    root = ET.fromstring(apidata.encode('utf-8'))
                    #Only continue if there are search results
                    if root.find('search')[3].text != '0':
                        #Get the first search result, hopefully the "right" one
                        for work in root.iter('work'):
                            data['average_rating'] = work.find('average_rating').text
                            data['ratings_count'] = work.find('ratings_count').text
                            best_book = work.find('best_book')
                            data['gr_book_id'] = best_book.find('id').text
                            data['title'] = best_book.find('title').text
                            data['gr_author_id'] = best_book.find('author')[0].text
                            data['author'] = best_book.find('author')[1].text
                            data['image_url'] = best_book.find('image_url').text
                            break
                except:
                    print 'Failed to parse API data for file: %s' % (item['filepath'])
                    parsefail += 1
                if parsefail != 0:
                    print 'Failed parsing API data for %s files' % (str(parsefail))
                #Check if we already have this API data
                bookexists = False
                for item in self.itemdata:
                    if item['gr_book_id'] == data['gr_book_id'] and data['filepath'] not in item['filepath']:
                        item['filepath'].append(data['filepath'])
                        bookexists = True
                        break
                if not bookexists:
                    #Make the filepath a list so we can add files later
                    data['filepath'] = [data['filepath']]
                    #Finally add the new item to itemdata
                    self.itemdata.append(data)

    def update(self):
        if path.isfile('db') and self.itemdata == []:
            with open('db', 'r') as f:
                self.itemdata = eval(f.read())
                
        #Check if the files still exists, else remove from data
        for item in self.itemdata:
            for f in item['filepath']:
                if not path.isfile(f):
                    item['filepath'].remove(f)
                    if item['filepath'] == []:
                        self.itemdata.remove(item)
        #Update the data, ie check for new files
        self.get_info_from_api(self.fileindex())
        #Write the data to the local "db"
        with open('db', 'w') as f:
            f.write(str(self.itemdata))

    def __init__(self):
        self.itemdata = []
        self.update()
