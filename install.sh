#!/bin/sh

# install dependencies
sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo -E apt-get install python-pip
sudo -E apt-get install python-qt4
sudo -E apt-get python install scipy