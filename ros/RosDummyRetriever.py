"""
This module is for development only - returning dummy values of ROBs checks
based on lists of testing values from test.roblists.py  

"""

import random
import sys

from test.roblists import robsDict
from Config import Config as conf
from ros.RosTree import Tree
from common.States import Error
from common.States import Alert
from common.States import Ok
from common.States import Inactive



class RosDummyRetriever(object):
    def __init__(self, logger):
        self.logger = logger
        self.states = (Error(), Alert(), Ok(), Inactive())
        

    def rosChecker(self, node, thLogger):
        """
        Returns random state ...
        
        """
        c = random.randrange(0, len(self.states))
        count = 2
        if not isinstance(self.states[c], Error):
            return self.states[c]
            
        # if it's Error, try again to see less red ...
        while count > 0:
            c = random.randrange(0, len(self.states))
            if not isinstance(self.states[c], Error):
                return self.states[c]
            count -= 1
            
        return self.states[c]
        

    def getTreesOfRosNames(self):
        """
        This method is merely for testing purposes ...
        This method takes names of IS objects as input from a testing file.
        
        """
        trees = {}
        for system in conf.SYSTEMS:
            try:
                robsList = robsDict[system]
                tree = Tree(system, self, self.logger)
                # constructing tree for a particular system
                for rob in robsList:
                    tree.add(rob)
                trees[system] = tree
                
                # check that number of leaves in leafNode list at each tree
                # is the same like number of items in the input list                
                if len(trees[system].leafNodes) != len(robsList):
                    self.logger.fatal("Number of leaf nodes don't agree "
                                      "with number of input items for "
                                      "'%s', exit" % system)
                    sys.exit(1)
            except KeyError:
                self.logger.error("System '%s' doesn't have testing ROS "
                                  "names available." % system)
        return trees
    
    
    def update(self):
        pass
