#!/bin/bash

#add user
USER_NAME=cloud
echo Add new user "$USER_NAME", please enter password below...
sudo adduser $USER_NAME
sudo usermod -a -G sudo,adm cloud

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

# install libgeo-osm-tiles-perl
sudo apt-get -y install libgeo-osm-tiles-perl

# install gcc for install peoplefinder (psutil) and uwsgi
sudo apt-get -y install gcc

# create env into home directory
sudo -H -u  $USER_NAME bash -c 'virtualenv '$HOME'/env'

# create directiories
sudo mkdir -p $PEOPLEFINDER_CONF_DIR
sudo mkdir -p $PEOPLEFINDER_LOG_DIR

# clone repository
sudo -H -u  $USER_NAME bash -c 'git clone https://github.com/nextgis/peoplefinder.git '$HOME'/peoplefinder'

# install application
sudo -H -u  $USER_NAME bash -c $HOME'/env/bin/pip install -e '$HOME'/peoplefinder/web'
sudo -H -u  $USER_NAME bash -c $HOME'/env/bin/pip install uwsgi'

sudo cp "$HOME/peoplefinder/web/development.example.ini" "$PEOPLEFINDER_CONF_DIR/config.ini"

# initialize db
sudo PYTHONPATH="${PYTHONPATH}:$HOME/peoplefinder" $HOME/env/bin/initialize_peoplefinder_db "$PEOPLEFINDER_CONF_DIR/config.ini"
sudo chown $USER_NAME $HOME/peoplefinder/storage/pf.sqlite

# configurate kannel
sudo cp "$HOME/peoplefinder/web/deploy/kannel" "/etc/default"
sudo cp "$HOME/peoplefinder/web/deploy/kannel.conf" "/etc/kannel"
sudo /etc/init.d/kannel restart

# configure osmobsc
sudo  $HOME/env/bin/python $HOME/peoplefinder/web/peoplefinder/scripts/configure_osmobsc.py
sudo sv restart osmo-trx osmo-bts osmo-nitb

# setup supervisor
sudo cp "$HOME/peoplefinder/web/deploy/peoplefinder.conf" "$SUPERVISOR_CONF_DIR"
sudo cp "$HOME/peoplefinder/web/deploy/comms_interface.conf" "$SUPERVISOR_CONF_DIR"
sudo supervisorctl reread
sudo supervisorctl update

# setup nginx
sudo cp "$HOME/peoplefinder/web/deploy/peoplefinder" "$NGINX_CONF_DIR/sites-available"
sudo ln -s "$NGINX_CONF_DIR/sites-available/peoplefinder" "$NGINX_CONF_DIR/sites-enabled"
sudo rm -f "$NGINX_CONF_DIR/sites-enabled/default"
sudo service nginx restart
