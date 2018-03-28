#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import setupLogging
import window


def logLevelResolver():
    logLevel = setupLogging.logging.WARNING
    if os.environ.get('logLevel') is None:
        return logLevel
    if os.environ['logLevel'] == 'DEBUG':
        logLevel = setupLogging.logging.DEBUG
    elif os.environ['logLevel'] == 'INFO':
        logLevel = setupLogging.logging.INFO
    return logLevel


def envHandler():
    logLevel = logLevelResolver()
    return logLevel


def run():
    app = window.QtGui.QApplication(sys.argv)
    sshFile = './stylesheet/darkOrange.stylesheet'
    with open(sshFile, 'r') as fh:
        app.setStyleSheet(fh.read())
    app.setStyleSheet(window.qdarkstyle.load_stylesheet_pyqt())
    _GUI = window.Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    logLevel = envHandler()
    setupLogging.setupLogging(logLevel)
    run()