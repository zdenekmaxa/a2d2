"""
Main A2D2 / R2D2 (ROD/ROS Data flow Display) file.
__author__ = Zdenek Maxa

"""

import os
myPath = os.path.abspath(os.path.dirname(__file__))
execfile(os.path.join(myPath, "Config.py"))

import sys
import threading
import time
import getopt
import logging

from Tkinter import Tk
from Tkinter import Menu
import tkMessageBox

from Config import Config as conf
from util.Logger import Logger
from TopLevelView import TopLevelView
from ros.RosDummyRetriever import RosDummyRetriever
from ros.RosRetrieverException import RosRetrieverException
from common.States import NotAssociated # created on-the-fly (metaclass)



class ThreadChecker(threading.Thread):
    """
    Thread implementation is completely independent on what
    actions may be run by it ...
    
    """
    def __init__(self, logLevel, action):
        self.actionToRun = action
        self.logger = Logger(name = "a2d2 thread",
                             logFile = conf.APPLICATION_LOG_FILE,
                             level = logLevel)
        threading.Thread.__init__(self)
        self.__stopFlag = False
        self.__bypass = False # if True, actions are skipped in periodic check
        self.logger.info("Initialised.")
        
        
    def run(self):
        while True:
            if self.__stopFlag:
                break
            time.sleep(3)
            if self.__stopFlag:
                break
            self.logger.debug("Running ...")
            
            if self.__bypass:
                self.logger.debug("Dummy loop, actual thread action bypassed.")
            else:                
                self.actionToRun(self.logger)
            
            self.logger.info("Loop finished, sleeping ...")
            
        self.logger.info("Completely finished.")            

        
    def setStop(self):
        self.logger.debug("Setting stop flag to True ...")
        self.__stopFlag = True
        self.logger.debug("Stop flag set to True.")
        
        
    def bypassExecution(self):
        self.__bypass = True
        
        
    def resumeExecution(self):
        self.__bypass = False



class Application(object):
    def __init__(self, tkRoot, retriever, logLevel, logger):
        self.logger = logger
        self.tkRoot = tkRoot
        self.retriever = retriever

        self.logger.info("Initializing a2d2 Application instance ...")
        
        self.tkRoot.protocol("WM_DELETE_WINDOW", self.__onClose)
        
        self.rosTrees = retriever.getTreesOfRosNames()
             
        # all windows (canvas instances) currently opened
        # updating of canvases will iterate over this
        self.__activeViews = {}
        # TopLevelView (TopLevelView canvas) component - main window
        # self.rosTrees must be initialised before TopLevelView is created
        self.__topLevelView = TopLevelView(self.tkRoot, conf.SYSTEMS, self,
                                           self.logger)
                
        self.__thChecker = ThreadChecker(logLevel, self.periodicChecker)
        self.__thChecker.start()
        self.logger.info("Thread started.")
        
        self.__makeMenu()
        
        self.logger.info("a2d2 Application instance initialised.")
        

    def __makeMenu(self):
        top = Menu(self.tkRoot) # top level
        self.tkRoot.config(menu = top) # set its menu option

        file = Menu(top)
        file.add_command(label = "Stop checks",
                           command = self.__thChecker.bypassExecution)
        file.add_command(label = "Resume checks",
                           command = self.__thChecker.resumeExecution)
        file.add_command(label = "Exit",
                           command = self.__onClose)
        top.add_cascade(label = "File", menu = file, underline = 0)
        
        
    def periodicChecker(self, thLogger):
        # here will be a list of actions to be periodically run
        # this method should use logger provided by the thread
        
        # update
        self.retriever.update()
        
        # 1st ROS checker
        for key in self.rosTrees:
            tree = self.rosTrees[key]
            for node in tree.leafNodes:
                node.action(node, thLogger) # this runs particular IS check
            # whole list of leaves processed, could update the tree
            tree.propagateStatesFromLeavesUp()
            
        # problems with canvas thread safety
        thLogger.info("Updating currently opened views ...")
        for view in self.__activeViews.values():
            view.updateView()
        
    
    def __onClose(self):
        if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?",
                                    parent = self.tkRoot):

            # in this method happens something (not clear exactly what) which
            # prevents successful completion (it if is concurrently running): 
            # Thread -> this.PeriodicChecker() -> updatingViews -> 
            # component.render() method -> self.canvas.itemconfig()
            # is just hangs if this method body runs concurrently ...
            # adding lock around to BaseView.updateView / stopUpdating()
            # doesn't help, this method, resp. Tkinter must internally,
            # do something for what self.canvas.itemconfig() never returns.
            # not completely understood, but if a single component update
            # is very quick (and it is), the freezes at closing are not seen
            # -> can however be easily reproduced by adding delay before
            # BaseView.updateView() k.render() call and trying to close
            # the application at the moment of updating its values ...
            
            self.logger.info("Setting stop updating flag on views ...")
            for view in self.__activeViews.values():
                view.stopUpdating()        
                                    
            self.logger.info("Stopping the ThreadChecker ...")
            self.__thChecker.setStop()
            
            count = 20 # number of tries to stop the thread checker
            while self.__thChecker.isAlive():
                self.logger.debug("Stopping the ThreadChecker (join) ...")
                self.__thChecker.join()
                count -= 1
                if count < 0:
                    break
                
            if self.__thChecker.isAlive():
                self.logger.info("Could not stop the ThreadChecker.")
            else:
                self.logger.info("ThreadChecker thread successfully stopped.")

            self.tkRoot.destroy()
            self.logger.warn("Application shut.")
            self.logger.close()
        
        
    def addActiveView(self, key, view):
        if key in self.__activeViews:
            self.logger.error("View '%s' is already among active windows, "
                              "not added." % key)
        else:
            self.__activeViews[key] = view
            self.logger.debug("View '%s' added among active windows." % key)
        
        
    def removeActiveView(self, key):
        try:
            del self.__activeViews[key]
            self.logger.debug("View '%s' removed from active windows." % key)
        except KeyError:
            self.logger.error("View '%s' was not among active windows, "
                              "error." % key)
  
    
    def activeViewsCount(self):
        return len(self.__activeViews)
    
    
    def isViewActive(self, key):
        return key in self.__activeViews
    
        
       
def printUsage(logLevels, modes):

    print """
%s
ROS/ROB IS object checker ...
Possible arguments:
    -p, --partition <name> (e.g. -p 'TileCosmic', default: '%s')
    -d, --debug <level> (options: '%s')
    -m, --mode <modename> (options: '%s')
""" % (sys.argv[0], conf.DEFAULT_PARTITION, logLevels.keys(), modes)



def getOptions(inputArgs):
    """Process command line arguments and return options.
    """
    partition = conf.DEFAULT_PARTITION
    logLevel = conf.LOGGING_LEVEL
    mode = conf.MODE
    
    logLevels = {"CRITICAL" : logging.CRITICAL, "INFO" : logging.INFO,
                 "DEBUG" : logging.DEBUG, "ERROR": logging.ERROR,
                 "FATAL" : logging.FATAL, "WARN" : logging.WARN}
    modes =  ('prod', 'production', 'devel', 'development')

    try:
        options, args = getopt.getopt(inputArgs, "hp:d:m:",
                ["help", "partition=", "debug=", "mode="])
    except getopt.GetoptError:
        print "Incorrect command line options, try --help"
        sys.exit(1)
    else:
        for o, a in options: # a is argument
            if o in ("-h", "--help"):
                printUsage(logLevels, modes)
                sys.exit(0)
            elif o in ("-p", "--partition"):
                partition = a
            elif o in ("-d", "--debug"):
                try:
                    logLevel = logLevels[a]
                except KeyError:
                    print "Unsupported logging level: '%s', using default." % a
            elif o in ("-m", "--mode"):
                if a in modes:
                    mode = a
                else:
                    print ("Unsupported mode '%s', using default '%s'" %
                          (a, conf.MODE))

    return (partition, logLevel, mode)
        


def main():
    (partition, logLevel, mode) = getOptions(sys.argv[1:])
    
    logger = Logger(name = "a2d2", logFile = conf.APPLICATION_LOG_FILE,
                    level = logLevel)
    logger.info("\n\n\n" + 78 * '=')
    
    logger.info("Options: IS partition: '%s' mode: '%s'" % (partition, mode))
    
    # create ROS retriever
    try:
        m = "Could not create an instance of retriever, reason: %s"
        if mode in ("prod", "production"):
            from ros.RosIsRetriever import RosIsRetriever
            rosRetriever = RosIsRetriever(partition, logger)
        elif mode in ("devel", "development"):
            rosRetriever = RosDummyRetriever(logger)
        else:
            raise RosRetrieverException("Unsupported mode: '%s'" % mode)
    except RosRetrieverException, ex:
        logger.fatal(m % ex)
        logger.close()
        sys.exit(1)
    except ImportError, ex:
        logger.fatal(m % ex)
        logger.fatal("Running '%s' mode, TDAQ release must be set up, e.g. by "
                     "sourcing /sw/atlas/tdaq/tdaq-02-00-02/installed/setup.sh "
                     "('tdaq_python' must be available from on command "
                     "line)." % mode)
        logger.close()
        sys.exit(1)
        
        
    tkRoot = Tk()
    geom = ("%sx%s+%s+%s" % (conf.GUI_WIDTH, conf.GUI_HEIGHT,
                            conf.GUI_OFF_X, conf.GUI_OFF_Y))
    logger.info("Main window geometry: '%s'" % geom)
    tkRoot.geometry(geom)
    # getting geometry info back: rootGeom = tkRoot.winfo_geometry()
    tkRoot.title("ROD/ROS data-flow display")

    try:
        Application(tkRoot, rosRetriever, logLevel, logger)
    except RosRetrieverException, ex:
        logger.fatal("Could not initialize the application, reason: %s" % ex)
        logger.close()
        sys.exit(1)

    tkRoot.mainloop()
    


if __name__ == "__main__":
    main()
