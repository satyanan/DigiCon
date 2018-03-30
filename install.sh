#!/bin/sh

# install dependencies
sudo -E apt-get install software-properties-common
sudo -E apt-add-repository universe
sudo -E apt-get update
sudo -E apt-get install python-pip
sudo -E apt-get install python-qt4
sudo -E apt-get install python-scipy
sudo -E apt-get install python-opencv
