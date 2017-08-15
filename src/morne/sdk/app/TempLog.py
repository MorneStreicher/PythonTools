import logging
from logging import StreamHandler, getLogger, Formatter
from logging.handlers import TimedRotatingFileHandler
import os
import sys

levels = {
            logging.DEBUG:    'debug',
            logging.INFO:     'info',
            logging.CRITICAL: 'critical'
         }

def getLog(dirname='', pathToLogs='..', streamLevel=logging.INFO, name=None):
    path = os.path.abspath(pathToLogs) + '/log/' + dirname


    # Setup the root logger to a file
    log = getLogger(name)
    log.setLevel(level=logging.DEBUG)

    # make sure the logging directory exists
    if not os.path.isdir(path):
        os.makedirs(path)

    for level in levels:
        addFileHandler(log, level, path + '/' + levels[level] + '.log')

    if name is None:
        addStreamHandler(log, streamLevel)
        log.progName = os.path.split(sys.argv[0])[1][:-3]
        log.info('-------------------------------------\n\n')
        log.info('Starting ' + log.progName)

    return log

def addStreamHandler(log, level):
    handler = StreamHandler()
    addHandler(log, level, handler)

def addFileHandler(log, level, name):
    addHandler(log, level, TimedRotatingFileHandler(name, when="MIDNIGHT", backupCount=90))

def addHandler(log, level, handler):
    handler.setLevel(level)
    handler.setFormatter(Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s'))
    log.addHandler(handler)


