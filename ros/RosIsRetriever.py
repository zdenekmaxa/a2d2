"""
Implementation of IS server communication.
Using 'ispy' Python wrapper for C++/Corba IS implementation.

Module queries a partition for ROS/ROB *DF* names (keys to objects).
Module retrieves values from IS and checks criteria of ROB values.
ROS consists of a number of ROBs.

Returns criteria result - state of a ROB (DataChannel).

"""

import re

from ispy import IPCPartition
from ispy import InfoReader

from Config import Config as conf
from ros.RosTree import Tree
from common.States import Error
from common.States import Alert
from common.States import Ok
from common.States import Inactive
from ros.RosCriteriaConfig import RosCriteriaConfig
from ros.RosRetrieverException import RosRetrieverException



class RosIsRetriever(object):
    def __init__(self, partitionName, logger):
        self.partitionName = partitionName
        self.logger = logger
        self.rcc = RosCriteriaConfig()
        self.states = (Error, Alert, Ok, Inactive)
        
        # try connecting to the IS, check if partition is valid
        self.partition = IPCPartition(self.partitionName)
        if not self.partition.isValid():
            m = "Partition '%s' is not valid." % self.partitionName
            raise RosRetrieverException(m)
 
        # get only ROB objects into the dictionary (DF is server), 
        # then pattern for objects names of interest
        self.readerRos = InfoReader(self.partition, "DF",
                                   ".*" + conf.ROS_IS_NAMES_PATTERNS[2])
        # get DFM (DataFlowManager object reader)
        self.readerDfm = InfoReader(self.partition, "DF", ".*DFM.*")
        
        self.readerRos.update()
        self.readerDfm.update()
        
        try:
            self.readerDfm.objects[self.rcc.objectKeyDfm]
        except KeyError:
            m = ("The partition '%s' is likely not combined, necessary "
                 "object '%s' missing." % (partitionName, self.rcc.objectKeyDfm))
            raise RosRetrieverException(m)

        
    def update(self):
        self.logger.info("Updating reader for IS objects ...")
        self.readerRos.update()
        self.readerDfm.update()
        self.logger.info("Updating IS reader finished.")

        
    def rosChecker(self, node, thLogger):
        # real IS object value checking against criteria RosCriteriaConfig
        # Values returned from self.readerRos.objects[] dictionary is
        # actually not a long string as I thought before (and confirmed by
        # Reiner) but is ISInfoAny class having __getattribute__() method
        
        # get DFM information (cleared events)
        try:
            dfm = self.readerDfm.objects[self.rcc.objectKeyDfm]
            cleared = dfm.__getattribute__(self.rcc.valueKeyDfmClearedEvents)
        except KeyError, ex:
            m = ("Problem getting / processing '%s', can't continue, reason: "
                 "%s." % (self.rcc.objectKeyDfm, ex))
            raise RosRetrieverException(m)

        # construct a dictionary with criteria names (IS DF subvalues names)
        # and their values
        crit = dict.fromkeys(self.rcc.valueKeysDf)
                
        resultState = Inactive() # starting with least priority state
        robInfo = "<empty>"
        try:
            robInfo = self.readerRos.objects[node.keyForIsObject]
            for valueName in crit: 
                value = robInfo.__getattribute__(valueName)
                crit[valueName] = value
        except (KeyError, AttributeError), ex:
            m = ("Problem getting / processing '%s', reason: '%s', "
                 "returning %s" % (node.keyForIsObject, ex, resultState))
            node.valueOfIsObject = "".join([m, "\n\n", "info:\n", str(robInfo)]) 
            return resultState
        
        # "cleared events" can't be added before - to be looked up
        # in DF.ROS objects since such values is not there, it's DFM value
        crit[self.rcc.valueKeyDfmClearedEvents] = cleared
        
        info = ""
        ok = Ok()    
        for c in self.rcc.criteria:
            condVal = c.condition % crit # filling in criteria value
            condRes = eval(condVal) # actual criteria evaluation
            info = " ".join([info, c.condition, str(condVal), str(condRes)])
            info = "".join([info, "\n"])
            if condRes:
                # this criteria is True
                if cmp(c.state, resultState) > 0: 
                    # its state has higher priority currently highest
                    # set result state, set this state 
                    resultState = c.state
                else:
                    # resultState is the same or highest priority
                    pass
            else:
                # condition is False - ok, just check if the currently
                # resulting state is not of higher priority, otherwise remains 
                if cmp(ok, resultState) > 0:
                    resultState = ok
        
        node.valueOfIsObject = info # or the whole str(robInfo)
        return resultState
                

    def getTreesOfRosNames(self):
        """
        Returns a dictionary (key is system name) with hierarchical
        (trees) structure of ROS/ROB DF IS object names.
        Combination of last two items of conf.ROS_IS_NAMES_PATTERNS
        patterns is enough to check all DF IS object keys against.
        examples:
        DF key: 'DF.ROS.ROS-LAR-EMBA-18.DataChannel4'
        patterns defined in: conf.ROS_IS_NAMES_PATTERNS
        
        """
        self.readerRos.update()
        trees = {}
        for systemName in conf.SYSTEMS:
            # need to use only the last two patterns
            
            patt = ("".join([conf.ROS_IS_NAMES_PATTERNS[1],
                           '.', conf.ROS_IS_NAMES_PATTERNS[2]]) %
                           { "subSystem" : systemName })
            self.logger.info("Using pattern: '%s'" % patt)
            compPatt = re.compile(patt)
            tree = Tree(systemName, self, self.logger)
            
            self.logger.info("Getting DF.ROS. * names for system '%s'" %
                             systemName)
        
            # constructing tree for a particular system
            # self.readerRos.objects is dictionary, iterating over keys
            for key in self.readerRos.objects:
                keyMatch = compPatt.search(key)
                if keyMatch:
                    tree.add(key) # is is ROB name now (*DataChannel)
            
            if len(tree.leafNodes) > 0: trees[systemName] = tree
            else: self.logger.warn("System '%s' not added into the tree "
                                   "(no leaves)." % systemName)

            m = ("System '%s' has %s leaf nodes (DataChannels/ROBs)" %
                 (systemName, len(tree.leafNodes))) 
            self.logger.info(m)
            
        return trees
