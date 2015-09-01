#!/bin/bash

#add user
USER_NAME=cloud
echo Add new user "$USER_NAME", please enter password below...
sudo adduser $USER_NAME
sudo usermod -a -G sudo,adm cloud
su -l $USER_NAME

# default values
HOME=/home/$USER_NAME
NGINX_CONF_DIR=/etc/nginx
SUPERVISOR_CONF_DIR=/etc/supervisor/conf.d
PEOPLEFINDER_CONF_DIR=/etc/peoplefinder
PEOPLEFINDER_LOG_DIR=/var/log/peoplefinder

# update package list
sudo apt-get update

# install python-dev
sudo apt-get -y install python-dev

# install nginx
sudo apt-get -y install python-software-properties
sudo add-apt-repository ppa:nginx/stable -y
sudo apt-get update
sudo apt-get -y install software-properties-common
sudo apt-get -y install nginx
sudo apt-get -y install kannel

# install pip & virtualenv
sudo apt-get -y install python-pip
sudo pip install virtualenv

# install supervisor
sudo apt-get -y install supervisor
sudo service supervisor restart

# install git
sudo apt-get -y install git

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

# configurate kannel
sudo cp "$HOME/peoplefinder/web/deploy/kannel" "/etc/default"
sudo cp "$HOME/peoplefinder/web/deploy/kannel.conf" "/etc/kannel"
sudo /etc/init.d/kannel restart

# configure osmobsc
$HOME/env/bin/configure_osmobsc
sudo sv restart osmo-nitb

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
