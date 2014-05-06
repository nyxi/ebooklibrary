Your Library
====

A basic Flask application getting data from Goodreads for ebook files in a specified directory with download links. It stores the data for the books in a local file called "db" to cut down on the number of API calls.

Uses the Bootstrap framework for the HTML/CSS stuff.

![ScreenShot](http://nyxi.eu/pics/projects/library.jpg)

Usage
-----
On the first run it can take a long time for the website to become available since it will do API calls for all your ebook files, progress can be tracked in the console.

1. pip install -r requirements.txt
2. Update settings in grdata.py
3. python front.py
