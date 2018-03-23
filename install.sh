#!/bin/sh

# install dependencies
sudp apt-get install pip
pip install pyqt4
sudo apt-get update
sudo -E pip install reportlab
sudo -E pip install qdarkstyle