"""
Testing of the application logic - app package
"""

execfile("../Config.py")

import pytest

from Config import Config as conf
from ros.RosDummyRetriever import RosDummyRetriever
from ros.RosTree import Tree
from util.Logger import Logger

"""
info (DataChannel items (ROBs) per system in testing data):
    robs: TIL items: 65
    robs: SCT items: 44
    robs: LAR items: 692
    robs: TRT items: 192
    robs: MDT items: 103
"""



def getListOfLeaves(node, leaves):
    for c in node.children.values():
        getListOfLeaves(c, leaves)
    # catch the name when it's leave node (0 children)
    if len(node.children) == 0:
        leaves.append(node.keyForIsObject)
        
    return leaves
    

def testTree():
    logger = Logger(name = "a2d2 test")

    retriever = RosDummyRetriever(logger)
    rosTrees = retriever.getTreesOfRosNames()
    
    for k, tree in rosTrees.items():
        tree.printTree()
        
        # test that number of leaf nodes agree with number of items in lists
        print "checking number of leaves in trees must agree with test source lists"
        listOfLeaves = getListOfLeaves(tree.root, [])
        print "%s %s == %s" % (k, len(tree.leafNodes), len(listOfLeaves))
        assert len(tree.leafNodes) == len(listOfLeaves)
        
        # test that all leaf nodes 'keyForIsObject' agree with all names in source lists
        for leaf in tree.leafNodes:
            if leaf.keyForIsObject not in listOfLeaves:
                py.test.fail("%s not in source list (system: %s)" %
                              (leaf.keyForIsObject, k))
