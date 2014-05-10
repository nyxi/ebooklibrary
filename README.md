Your Library
====

A basic Flask application providing easy access to your ebook backups on disk with some nice data from Goodreads. Stores the data about each book in local file called "db" to cut down on the number of API calls.

Uses the Bootstrap framework for the HTML/CSS stuff.

![ScreenShot](http://nyxi.eu/pics/projects/library.jpg)

Usage
-----
On the first run it can take a long time for the website to become available since it will do API calls for all your ebook files, progress can be tracked in the console.

1. pip install -r requirements.txt
2. Edit and save "config.sample" as "config"
3. python front.py

By default the web page is served on port 5001.
