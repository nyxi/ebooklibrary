#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, render_template, abort, send_from_directory
import grdata
from os import path

app = Flask(__name__)
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

@app.route('/', methods=['GET'])
def index():
    data.update()
    titles, authors = sortselects(data.itemdata)
    return render_template('index.jinja2', data=data.itemdata, authors=authors, titles=titles)

@app.route('/author/<author>', methods=['GET'])
def authorpage(author):
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
