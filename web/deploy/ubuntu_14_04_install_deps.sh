#!/bin/bash

#add user
USER_NAME=cloud
echo Add new user '$USER_NAME', please enter password below...
sudo adduser $USER_NAME
sudo usermod -a -G sudo,adm cloud

# default values
HOME=/home/$USER_NAME
NGINX_CONF_DIR=/etc/nginx
SUPERVISOR_CONF_DIR=/etc/supervisor/conf.d
PEOPLEFINDER_CONF_DIR=/etc/peoplefinder
PEOPLEFINDER_LOG_DIR=/var/log/peoplefinder

sudo apt-get install aptitude
sudo apt-get install python-dev

# install nginx
sudo apt-get install python-software-properties
sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install software-properties-common
sudo apt-get install nginx

# install pip & virtualenv
sudo aptitude install python-pip
sudo pip install virtualenv

# install supervisor
sudo aptitude install supervisor
sudo service supervisor restart

# create env into home directory
virtualenv $HOME/env

# create directiories
sudo mkdir -p $PEOPLEFINDER_CONF_DIR
sudo mkdir -p $PEOPLEFINDER_LOG_DIR

# clone repository
git clone https://github.com/nextgis/peoplefinder.git "$HOME/peoplefinder"

export PYTHONPATH="${PYTHONPATH}:$HOME/peoplefinder"

# install application
$HOME/env/bin/pip install -e $HOME/peoplefinder/web
$HOME/env/bin/pip install uwsgi
sudo cp "$HOME/peoplefinder/web/development.example.ini" "$PEOPLEFINDER_CONF_DIR/config.ini"

# initialize db
$HOME/env/bin/initialize_peoplefinder_db "$PEOPLEFINDER_CONF_DIR/config.ini"

# setup supervisor
sudo cp "$HOME/peoplefinder/web/deploy/peoplefinder.conf" "$SUPERVISOR_CONF_DIR"
sudo cp "$HOME/peoplefinder/com_interface/comms_interface.conf" "$SUPERVISOR_CONF_DIR"
sudo supervisorctl reread
sudo supervisorctl update

# setup nginx
sudo cp "$HOME/peoplefinder/web/deploy/peoplefinder" "$NGINX_CONF_DIR/sites-available"
sudo ln -s "$NGINX_CONF_DIR/sites-available/peoplefinder" "$NGINX_CONF_DIR/sites-enabled"
sudo rm -f "$NGINX_CONF_DIR/sites-enabled/default"
sudo service nginx restart
