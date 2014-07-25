#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from flask import abort, Flask, redirect, render_template
from flask import request, send_from_directory, session
import grdata
import os
import subprocess
from werkzeug import secure_filename

#Get settings from the config file
config = ConfigParser.SafeConfigParser()
config.read('config')
KSN = config.get('web', 'kindleserial')
PASSWORD = config.get('web', 'password')
PORT = int(config.get('web', 'port'))
ALLOWED_FORMATS = config.get('data', 'formats').split(',')
BOOKDIR = config.get('data', 'bookdir')
#Configure Flask
app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config['UPLOAD_FOLDER'] = 'static/tmp'
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
        if request.form['password'] == PASSWORD:
            session['logon'] = True
            return redirect('/')
    return render_template('login.jinja2', fail=True)

@app.route('/', methods=['GET'])
def index(success=None, error=None):
    if not 'logon' in session:
        return redirect('/login/')
    data.update()
    titles, authors = sortselects(data.itemdata)
    return render_template('index.jinja2', data=data.itemdata, authors=authors, titles=titles, success=success, error=error)

@app.route('/', methods=['POST'])
def upload():
    if not 'logon' in session:
        return redirect('/login/')
    bookfile = request.files['file']
    if bookfile:
        if os.path.splitext(bookfile.filename)[1] in ALLOWED_FORMATS:
            filename = secure_filename(bookfile.filename)
            try:
                bookfile.save('%s/%s' % (app.config['UPLOAD_FOLDER'], filename))
            except:
                error = 'Error saving uploaded file to disk, permissions?'
                return index(error=error)
            if KSN == 'no':
                try:
                    os.rename('%s/%s' % (app.config['UPLOAD_FOLDER'], filename), '%s/%s' % (BOOKDIR, filename.replace('_', ' ')))
                    success = 'Successfully uploaded the file'
                    return index(success=success)
                except:
                    error = 'Could not move the file from the temporary upload location to the books directory, permissions issue?'
                    return index(error=error)
            try:
                infile = '%s/%s' % (app.config['UPLOAD_FOLDER'], filename)
                outdir = app.config['UPLOAD_FOLDER']
                subprocess.call(['./dedrm.sh', KSN, infile, outdir])
                os.remove(infile)
                newfile = '%s_nodrm%s' % (os.path.splitext(filename)[0], os.path.splitext(filename)[1])
                if os.path.isfile('%s/%s' % (outdir, newfile)):
                    os.rename('%s/%s' % (outdir, newfile), '%s/%s' % (BOOKDIR, filename.replace('_', ' ')))
                    success = 'Successfully uploaded the file'
                    return index(success=success)
                else:
                    error = 'Error at dedrm stage'
                    return index(error=error)
            except:
                error = 'Error at dedrm stage'
                return index(error=error)
        else:
            error = 'File format not allowed'
            return index(error=error)
    else:
        error = 'Nothing uploaded?'
        return index(error=error)

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
                        return send_from_directory(os.path.split(f)[0], os.path.split(f)[1], as_attachment=True, attachment_filename=os.path.split(f)[1])
        abort(404)
    else:
        abort(404)

@app.route('/isbn/', methods=['GET'])
def isbn_editor(success=None, error=None):
    if not 'logon' in session:
        return redirect('/login/')
    with open('isbn', 'r') as f:
        isbn = f.read()
    return render_template('index.jinja2', isbn=isbn, success=success, error=error, noresults=data.noresults)

@app.route('/isbn/', methods=['POST'])
def isbn_edit():
    if not 'logon' in session:
        return redirect('/login/')
    if 'isbn' in request.form:
        try:
            with open('isbn', 'w') as f:
                f.write(request.form['isbn'])
            success = 'Successfully updated the isbn file, result shown below.'
            return isbn_editor(success=success)
        except:
            error = 'Something went wrong when updating the file, permissions?'
            return isbn_editor(error=error)
    else:
        error = 'No isbn post data to process'
        return isbn_editor(error=error)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
