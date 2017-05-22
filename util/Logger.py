"""
Python wrapper class for logging module.
When in DEBUG mode, prints out exception tracebacks.

__author__ = "Zdenek Maxa"

"""

import sys
import traceback
import logging


class Logger(logging.getLoggerClass()):
    """Customised Logger. Logging either to console or into a file."""

    def __init__(self, name = "Logger", logFile = None, level = logging.DEBUG):
        # handler for logging into a file, optional
        self.logFileHandler = None

        logging.Logger.__init__(self, name) # initialise logger, necessary!

        self.setLevel(level)  # should be set for further created handlers

        # %(name)-12s gives name as given here: name = "Logger"
        fs = "%(asctime)s %(name)-5s %(levelname)-7s %(message)s"
        formatter = logging.Formatter(fs)

        
        # logging to console, sys.stdout, perhaps turned off if 
        # file is not provided: if not logFile: ... then else for FileHandler 
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        self.addHandler(console)
        
        if logFile:
            # log file has been specified, log into file rather than console
            self.logFileHandler = logging.FileHandler(logFile)
            self.logFileHandler.setLevel(level)
            self.logFileHandler.setFormatter(formatter)
            self.addHandler(self.logFileHandler)



    def close(self):
        # can't be put into __del__() - gives error (file already closed)
        self.debug("Logger closing.")
        if self.logFileHandler:
            self.logFileHandler.flush()
            self.logFileHandler.close()


    def getTracebackSimple(self):
        """
        Returns formatted traceback of the most recent exception.
        
        """
        # sys.exc_info() most recent exception
        trace = traceback.format_exception(*sys.exc_info())
        tbSimple = "".join(trace)  # may want to add '\n'
        return tbSimple


    def error(self, msg, traceBack = False):
        if traceBack:
            # get last exception traceback
            # add traceback below the normal 'msg' message
            msg = ("%s\n\n%s" % (msg, self.getTracebackSimple()))
        logging.Logger.error(self, msg)


    def fatal(self, msg, traceBack = False):
        if traceBack:
            # get last exception traceback
            # add traceback below the normal 'msg' message
            msg = ("%s\n\n%s" % (msg, self.getTracebackSimple()))
        logging.Logger.fatal(self, msg)


    def __del__(self):
        pass
