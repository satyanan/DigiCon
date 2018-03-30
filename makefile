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

package:
	tar -cvf ./digicon.tar.gz ./src ./classifier ./pre_proc ./autocorrect install.sh requirements.txt

install:
	rm -rf ./digicon
	tar -xvf digicon.tar.gz -C ./
	mkdir -p ./temp/output/intermediateImgs
	sudo chmod +x install.sh
	sudo -E ./install.sh
	sudo -E pip install -r requirements.txt
	
build: install

clean:
	rm -rf temp/*
	rm -rf test/*

envsetup:
	mkdir -p ./temp/output/intermediateImgs
	
run: envsetup
	export logLevel="WARNING"
	cd ./src/ &&	python main.py

rundebug: envsetup
	export logLevel="DEBUG"
	cd ./src && python2 main.py

runbatch:
