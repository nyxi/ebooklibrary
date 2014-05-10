#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import abort, Flask, redirect, render_template
from flask import request, send_from_directory, session
import grdata
from os import path, urandom
import ConfigParser

#Get password from the config file
config = ConfigParser.SafeConfigParser()
config.read('config')
password = config.get('web', 'password')
#Configure Flask
app = Flask(__name__)
app.secret_key = urandom(64)
#Create our data object
data = grdata.Data()

def sortselects(itemdata):
    authors = []
    titles = []
    for item in itemdata:
        author = '%s %s' % (item['author'], item['gr_author_id'])
        title = '%s %s' % (item['title'], item['gr_book_id'])
        if not author in authors:
            authors.append(author)
        if not title in titles:
            titles.append(title)
    return sorted(titles), sorted(authors)


@app.route('/login/', methods=['GET'])
def loginpage():
    if 'logon' in session:
        return redirect('/')
    return render_template('login.jinja2')

@app.route('/login/', methods=['POST'])
def login():
    if 'password' in request.form:
        if request.form['password'] == password:
            session['logon'] = True
            return redirect('/')
    return render_template('login.jinja2', fail=True)

@app.route('/', methods=['GET'])
def index():
    if not 'logon' in session:
        return redirect('/login/')
    data.update()
    titles, authors = sortselects(data.itemdata)
    return render_template('index.jinja2', data=data.itemdata, authors=authors, titles=titles)

@app.route('/author/<author>', methods=['GET'])
def authorpage(author):
    if not 'logon' in session:
        return redirect('/login/')
    filteredresults = []
    for item in data.itemdata:
        if item['gr_author_id'] == author and item not in filteredresults:
            filteredresults.append(item)
    if not filteredresults:
        abort(404)
    titles, authors = sortselects(data.itemdata)
    return render_template('index.jinja2', data=filteredresults, authors=authors, titles=titles)

@app.route('/download', methods=['GET'])
def download():
    if not 'logon' in session:
        return redirect('/login/')
    if 'id' in request.args and 'format' in request.args:
        gr_book_id, filetype = request.args['id'], request.args['format']
        for item in data.itemdata:
            if 'gr_book_id' in item and item['gr_book_id'] == gr_book_id:
                for f in item['filepath']:
                    if f.endswith(filetype) and '.%s' % (filetype) in data.FORMATS:
                        return send_from_directory(path.split(f)[0], path.split(f)[1], as_attachment=True, attachment_filename=path.split(f)[1])
        abort(404)
    else:
        abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
