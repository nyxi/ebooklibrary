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

    def isbn_update(self):
        isbnlist = []
        if path.isfile('isbn'):
            with open('isbn', 'r') as f:
                for line in f.read().splitlines():
                    if line[0] == '#':
                        continue
                    words = line.split()
                    isbnlist.append([' '.join(words[0:-1]), words[-1]])
        return isbnlist

    def is_isbn(self, filenoext):
        for item in self.isbnlist:
            if item[0] == filenoext:
                return item[1]
        return False

    def cleanup_isbn_clones(self):
        for isbn_item in self.itemdata:
            if isbn_item['isbn']:
                for possible_clone in self.itemdata:
                    for f in isbn_item['filepath']:
                        if f in possible_clone['filepath'] and not possible_clone['isbn']:
                            self.itemdata.remove(possible_clone)

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
            data['isbn'] = self.is_isbn(data['filenoext'])
            filestocheck.append(data)
        return filestocheck

    def decide_api_calls(self, filestocheck):
        for data in filestocheck:
            doapicall = True
            for item in self.itemdata:
                dupcheck = []
                for f in item['filepath']:
                    if f in dupcheck:
                        item['filepath'].remove(f)
                    else:
                        dupcheck.append(f)
                    if data['filepath'] == f and (not data['isbn'] or data['isbn'] == item['isbn']):
                        doapicall = False
                        break
                if not doapicall:
                    break
            if doapicall:
                self.api_call(data)

    def api_call(self, data):
        #Call to the API search function
        try:
            if not data['isbn']:
                #Get rid of some unnecessary chars in the search string
                q = data['filenoext'].replace(',', ' ')
                q = q.replace('-', ' ')
                q = ' '.join(q.split())
            else:
                q = data['isbn']
            payload = {'key':self.APIKEY, 'q':q}
            #Be nice and don't hammer the API to oblivion
            sleep(3)
            #Send the API request
            r = requests.get(self.APIURL, params=payload, timeout=self.TIMEOUT)
            #print '[%s] Making an API call to Goodreads' % (apicalls)
            print 'API call: %s' % (r.url)
            apidata = r.text
        except:
            print 'Goodreads took longer than %s seconds to respond, aborting remaining API calls' % (self.TIMEOUT)
            return False
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
            return False
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
        self.isbnlist = self.isbn_update()

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
        self.decide_api_calls(self.fileindex())
        #Remove items without ISBN if one of their files
        #are also in a item with ISBN
        self.cleanup_isbn_clones()
        #Write the data to the local "db"
        with open('db', 'w') as f:
            f.write(str(self.itemdata))

    def __init__(self):
        self.itemdata = []
        self.update()
