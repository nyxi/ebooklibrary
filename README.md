Your Library
====

A basic Flask application providing easy access to your ebook backups on disk with some nice data from Goodreads. Stores the data about each book in local file called "db" to cut down on the number of API calls.

Uses the Bootstrap web framework for the HTML/CSS stuff.

Up to date screenshot always available [here](http://nyxi.eu/pics/projects/library.jpg).
![ScreenShot](http://nyxi.eu/pics/projects/library.jpg)

Usage
-----
On the first run it can take a long time for the website to become available since it will do API calls for all your ebook files, progress can be tracked in the console.

Step 3 is __optional__ but necessary to remove DRM from Amazon ebooks.

1. `pip install -r requirements.txt`
2. Edit and save `config.sample` as `config`
3. Download the dedrm tools from [Apprentice Alf](http://apprenticealf.wordpress.com/) and edit `dedrm.sh` accordingly
4. `python front.py`

For a more solid deployment see the example further down with Supervisor, uWSGI and nginx.

File names
-----
The application works best if you name your files as below:
`<a_surname>, <a_firstname> - <title>.<format>`

Using underscores instead of white space is fine.

Deploying with nginx and friends
-----
This procedure replaces step 4 from the "Usage" section.

1. `pip install supervisor uWSGI`
2. Install nginx
3. Put the below somewhere, for instance `/path/to/this/repo/uwsgi_conf.yaml`
```
uwsgi:
  socket: 127.0.0.1:2424
  master: true
  wsgi: front:app
  processes: 4
  threads: 2
  log-syslog: true
```
4. Put the below in for instance `/etc/nginx/sites-available/library`
```
server {
    listen       80;
    server_name  library.example.com;
    client_max_body_size 5M;
    location / { try_files $uri @app; }
    location @app {
        uwsgi_pass 127.0.0.1:2424;
        include uwsgi_params;
    }
}
```
5. Finally the config for Supervisord in `/etc/supervisord.conf`
```
[unix_http_server]
file=/tmp/supervisor.sock
[supervisord]
logfile=/tmp/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[program:library]
command=/usr/local/bin/uwsgi --yaml uwsgi_conf.yaml
directory=/path/to/this/repo <<<<< CHANGE THIS
numprocs=1
stopsignal=INT
```
6. Launch Supervisord (which should in turn launch uWSGI): `supervisord -c /etc/supervisord.conf`
7. Restart nginx: `service nginx restart`
