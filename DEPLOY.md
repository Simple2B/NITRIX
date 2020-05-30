# NITRIX. Deploy instruction
This instruction for deploy Flask application.

**Prerequisites:**
* OS: Ubuntu 18.*
* Web Server: Nginx
* Python3
* [uWSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)


## Deploy from github

Choice folder for deploy. E.g. : ~/NITRIX/
For user **inv** it will be folder /home/inv/NITRIX
Create folder:
```
mkdir ~/NITRIX
```
Project NITRIX placed in GitHub repository [here](https://github.com/simple2b/NITRIX).
Let's download the project from GitHub:
```
cd ~/NITRIX
git clone https://github.com/Simple2B/NITRIX.git .
```

## Prepare environment
Setup necessaries packages:
```
sudo apt-get install nginx python3 virtualenv
```
Set correct rights for the project folder:
```
sudo chown -Rc inv:www-data ~/NITRIX
sudo chmod -R 0755 ~/NITRIX
```
Now, create python virtual environment:
```
cd ~/NIRTIX
virtualenv -p python3 .venv
pip install -r requirements.txt
deactivate
```

## Configure WSGI
We use uWSGI service from python virtual environment.
Activate virtual environment and setup actual packages:
```
sudo apt-get install python3-dev build-essential
cd ~/NIRTIX
source .venv/bin/activate
pip install uwsgi
```
Verify **uwsgi.ini** file (WSGI configuration) in project folder:
```ini
[[uwsgi]
# path to project foled
base = /home/inv/NITRIX
# module name
module = flask_app:app
# virtual env
chdir = %(base)
home = %(base)/.venv

master = true
# number of processes uWSGI
processes = 5
# user name for process
uid = inv
gid = www-data
socket = /tmp/nitrix-uwsgi.sock
chmod-socket = 660

# remove temporary files on service stop
vacuum = true
# path to log file
logto = /tmp/uwsgi.log

die-on-term = true
wsgi-disable-file-wrapper = true

```
Line `base = /home/inv/NITRIX` must contain correct path to project folder.
Line `uid = inv` must contain correct user name.

## Create Linux Service

Create file `/etc/systemd/system/nitrix-uwsgi.service` with follow content:
```ini
[[Unit]
Description=uWSGI instance to serve flask-uwsgi project
After=network.target

[Service]
User=inv
Group=www-data
WorkingDirectory=/home/inv/NITRIX
Environment="PATH=/home/inv/NITRIX/.venv/bin"
ExecStart=/home/inv/NITRIX/.venv/bin/uwsgi --ini /home/inv/NITRIX/uwsgi.ini

[Install]
WantedBy=multi-user.target
```

#### Attention! This file content for:
* User: `inv`
* Project folder `/home/inv/NITRIX`
You need fix it if you have another user name or/and project folder

Run service:
```
sudo systemctl start nitrix-uwsgi
```
Activate service
```
sudo systemctl enable nitrix-uwsgi
```

## Nginx configuration

Create file `/etc/nginx/sites-available/nitrix.conf` with following content:
```
upstream uwsgi_nitrix_upstream {
    server unix:/tmp/nitrix-uwsgi.sock;
}

server {
    listen 8080;
    server_tokens off;
    server_name inventory.nitrix.ch;

     location / {
         include uwsgi_params;
         uwsgi_pass uwsgi_nitrix_upstream;
     }

     location /static {
         root /home/inv/NITRIX/app/static;
     }

}
```
This Nginx configuration for run NITRIX project on port 8080. You can change follow values:
* `listen 8080` -- set here correct port
* server_name inventory.nitrix.ch; -- outgoing server name
* root /home/inv/NITRIX/app/static; -- path to static files (inside project folder)

Activate this Nginx configuration:
```
sudo ln -s /etc/nginx/sites-available/nitrix.conf /etc/nginx/sites-enabled/
```
Check if our configuration file is OK:
```
sudo nginx -t
```
Reload Nginx configuration:
```
sudo systemctl reload nginx
```
