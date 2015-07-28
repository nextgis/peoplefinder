#!/bin/bash

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

# create env into cloud directory
cd ~
virtualenv env

# install supervisor
sudo aptitude install supervisor
sudo service supervisor restart

# clone repository
git clone https://github.com/nextgis/peoplefinder.git

# install application
cd ~
./env/bin/pip install -e ./peoplefinder/web

# install uwsgi
./env/bin/pip install uwsgi
