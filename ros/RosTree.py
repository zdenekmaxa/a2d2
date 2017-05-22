"""
Implementation of Tree data structure describing hierarchy of ROS names
for a given subsystem.

"""

import sys
import re

from Config import Config as conf
from util.Logger import Logger
from View import View
from ros.RosRetrieverException import RosRetrieverException
from ros.RosView import RosView
from ros.RobView import RobView
from common.States import Inactive
from common.States import NotAssociated



class Checker(object):
    def __init__(self, retriever):
        self.retriever = retriever
        
        
    def update(self):
        """
        In production, when getting data from IS, this method
        invokes InfoReader.update() method to update data from IS.
        
        """
        self.retriever.update()
        
        
    def __call__(self, node, thLogger):
        """Called from a thread, using thread logger."""
        #thLogger.debug("Checker called on %s" % node)
        try:
            newState = self.retriever.rosChecker(node, thLogger)
        except RosRetrieverException, ex:
            thLogger.fatal(ex)
        else:
            if cmp(newState, node.state) != 0: # was there a change?
                node.state = newState
                thLogger.debug("State changed: %s" % node)
            else:
                pass



class Tree(object):
    def __init__(self, name, retriever, logger = Logger(name = "ROS tree")):
        self.root = Node(name) # no parent argument - root node
        self.logger = logger
        
        # classes to be viewed children on particular view levels with
        self.viewers = (View, RosView, RobView)
        
        pats = conf.ROS_IS_NAMES_PATTERNS 
        self.compPatts = [re.compile(p % { "subSystem" : name }) for p in pats]
        
        # holds list of leaf nodes references for quicker periodic checking
        self.leafNodes = []
        
        # create instance of the Checker class (one par ROS system tree)
        self.checker = Checker(retriever)
        

    def __str__(self):
        return ("tree (root node): '%s' (%s leaf nodes)" %
                (self.root, len(self.leafNodes)))
        

    def add(self, rob):
        # example names of DF IS objects
        # "DF.ROS.ROS-SCT-BA-00.DataChannel8"
        # "DF.ROS.ROS-SCT-BC-01.DataChannel4"
        # "DF.ROS.ROS-LAR-EMECC-04.DataChannel0"
        # "DF.ROS.ROS-LAR-EMECA-00.DataChannel10"
        
        # this list will hold partial names:
        # DF.ROS.ROS-SCT-BA-00.DataChannel8:
        # 1) SCT-BA 2) SCT-BA-00 3) SCT-BA-00.DataChannel8   
        names = []
        for cp in self.compPatts:
            m = cp.search(rob)
            if m:
                n = rob[m.start():m.end()]
                names.append(n)
        
        if len(names) != len(self.compPatts):
            self.logger.fatal("RosTree names error - number of "
                              " names != number of patterns, exit.")
            sys.exit(1)
            
        #self.__addToTree(names, rob) # longer, more readable solution
        self.__addToTreeRec(names, rob) # the same, no duplication loop solution 
        
    def __addToTreeRec(self, names, fullName):
        node = self.root
        for (name, viewer) in zip(names, self.viewers):
            try:
                nodeFollower = node.children[name]
            except KeyError:
                nodeFollower = Node(name, node)
                nodeFollower.viewerForChildren = viewer
                node.children[name] = nodeFollower
            finally:
                node = nodeFollower
        else:
            # at the very last node (leaf) ; have to store the reference
            node.keyForIsObject = fullName
            node.action = self.checker
            self.leafNodes.append(node)
            
                        
    def printTree(self):
        self.__printTree(self.root)
            
            
    def __printTree(self, node):
        if len(node.children) > 0:
            print "node: ", node.name
            print "\t%s\n" % self.__getChildrenInfo(node)
            for c in node.children.values():
                self.__printTree(c)
            
            
    def __getChildrenInfo(self,  node):
        s = ""
        for c in node.children.values():
            s += "".join([c.name, "  "])
        return s
        
        
    def propagateStatesFromLeavesUp(self):
        """
        Propagate values up the tree from leaves ...
        This method is called once the whole list of leaves was processed
        and update their values ... should be done recursively ...
        now (ugly) relying on the 3 levels depth ...
        test / observe properly though
        TODO: recursion here if more levels are to be nested
        """
        self.logger.debug("Updating: %s" % self)
        
        for nodes1 in self.root.children.values():
            for nodes2 in nodes1.children.values():
                for leaf in nodes2.children.values():
                    #2nd level
                    nodes2.setState(leaf.state)
                #print "all leaves processed
                #1st level
                nodes1.setState(nodes2.state) 
            #root level
            self.root.setState(nodes1.state)    
                


class Node(object):
    def __init__(self, name, parent = None):
        self.parent = parent  # if None, it's a root node
        self.children = {}    # key: names, values: Node instances
                                   
        self.name = name      # name of this node
        
        # used only at leaves - IS key - name of DF object (but these
        # attributes are generally available at all nodes)
        self.keyForIsObject = None
        self.valueOfIsObject = "<empty string>" # set by the IS checker
        
        self.viewerForChildren = None
        
        self.state = Inactive() # default state
        
        # action (callable) to perform
        self.action = None
        
        # this serves as container for states objects - when container
        # as many states as a node has children, contents of this
        # container is evaluated and highest priority state set
        # (means method setState() has been called from each child)
        self.__statesMem = []
        
    
    def __str__(self):
        r = "node: '%s' state: %s" % (self.name, self.state)
        if self.keyForIsObject:
            return "".join([r, " (leaf) IS key: '%s'" % self.keyForIsObject])
        return r
    
    
    def setState(self, newState):
        if len(self.children) > 0: # is node, not leave
            self.__statesMem.append(newState)
            if len(self.__statesMem) == len(self.children):
                # all children tried to change my state
                stateHighest = NotAssociated()
                for state in self.__statesMem:
                    if cmp(state, stateHighest) > 0:
                        stateHighest = state
                self.__statesMem = [] # empty the container
                self.state = stateHighest
