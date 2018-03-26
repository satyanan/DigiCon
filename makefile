#
# Makefile for DigiCon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

PYTHON       = python
SPHINXOPTS   =
PAPER        =
SOURCES      =

.PHONY: help checkout update build html htmlhelp latex text changes linkcheck \
	suspicious coverage doctest pydoc-topics htmlview clean dist check serve \
	autobuild-dev autobuild-stable

help:
	@echo "	Please use \`make <target>' where <target> is one of"
	@echo "	clean				to remove temporary files"
	@echo " install			to install the dependecies"
	@echo " build				to install dependecies and also build the project"
	@echo " test				to run all tests"
	@echo " unittest		to run only unit tests"
	@echo " sanitytest	to run only sanity tests"
	@echo " functest		to run only functionality tests"

install:
	rm -rf temp/*
	mkdir temp
	mkdir temp/output
	pip install -r requirements.txt
	sudo chmod +x install.sh
	sudo -E ./install.sh

build: install


clean:
	rm -rf temp/*
	rm -rf test/*

run:
	export logLevel="WARNING"
	cd ./src/ &&	python main.py

rundebug:
	cd ./src
	export logLevel="DEBUG"
	python2 main.py

runbatch:
