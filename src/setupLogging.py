import sys
import os
import logging

# Sets up logging based on the input parameter logging. Log level defaults to logging.WARN
def setupLogging(logLevel=logging.WARNING):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    loggerHandler = logging.StreamHandler(sys.stdout)
    loggerHandler.setLevel(logLevel)
    loggerFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    logger.addHandler(loggerHandler)

if __name__ == '__main__':
  setupLogging()