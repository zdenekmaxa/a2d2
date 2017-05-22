"""
Implementation of Top level view Canvas.
Currently only having ROD and ROS blocks.

Should encapsulate all graphical part and just provide methods for
manipulating graphical elements (e.g. ROS boxes).

"""

from Tkinter import Canvas
from Tkinter import YES
from Tkinter import BOTH
from Tkinter import PhotoImage
import tkMessageBox

from Config import Config as conf
from BaseView import BaseView
from BaseView import Box
from BaseView import RenderableBox
from BaseView import Line
from View import View
from BaseView import DoubleClickHandler
from common.States import Inactive
from common.States import NotAssociated



class TopLevelView(BaseView):    
    TEXT_LABEL_OFFSET = 35
    ROD_BOX_START_X = 50
    ROD_BOX_START_Y = 45
    ROD_BOX_WIDTH = 70
    ROD_BOX_HEIGHT = 25
    ROD_BOX_VERTICAL_OFFSET = 10
    
    # other values are the same like for the ROD boxes
    ROS_BOX_START_X = 150
    ROS_BOX_START_Y = 45

    
    def __init__(self, tkRoot, systems, app, logger):
        BaseView.__init__(self, tkRoot, app, logger)
        
        self.systems = systems # names of all subsystems
        
        # Canvas options width, height seem not necessary ...
        self.canvas = Canvas(self.tkRoot, bg = BaseView.CANVAS_BG_COLOR)
        self.canvas.pack(expand = YES, fill = BOTH)
        
        self.__createRodBoxes()
        self.__createRosBoxes()
        self.__createRodRosLines()
        
        self.name = "TOP" # name of this special view
        self.app.addActiveView(self.name, self) # special top view

        # add logo
        logo = PhotoImage(file = "doc/logo.gif")
        self.canvas.create_image(conf.GUI_WIDTH - 20,
                                 conf.GUI_HEIGHT - 20, image = logo)
        self.canvas.image = logo # keep a reference, otherwise it won't appear
        
    
    def __openRosDetailedView(self, comp):
        try:
            rosTree = self.app.rosTrees[comp.name]
            # every view (except for TopLevelView) has a tree node
            # acting as root for such particular view
            treeRootNode = rosTree.root
            v = View(self.tkRoot, self.app, comp, treeRootNode, self.logger)
            v.createContent()
            self.logger.debug("View created for '%s'" % comp)
        except KeyError:
            m = "ROS data n/a for '%s'" % comp
            self.logger.warn(m)
            tkMessageBox.showwarning("Quit", m, parent = self.tkRoot)
        

    def openDetailedView(self, comp):
        if comp.group == "ROS":
            # check if view which is to be open has not been opened already
            if self.app.isViewActive(comp.name):
                m = ("View '%s' is already among active windows, "
                    "not created." % comp.name)
                self.logger.warn(m)
                tkMessageBox.showwarning("Quit", m, parent = self.tkRoot)
            else:
                self.__openRosDetailedView(comp)
        else:
            m = "No view available for '%s' " % comp
            self.logger.warn(m)
            tkMessageBox.showwarning("Quit", m, parent = self.tkRoot)
        
        
    def __createRodBoxes(self):
        state = NotAssociated()
        group = "ROD" # title
        self.canvas.create_text(TopLevelView.ROD_BOX_START_X +
                                TopLevelView.TEXT_LABEL_OFFSET,
                                TopLevelView.ROD_BOX_START_Y -
                                TopLevelView.ROD_BOX_HEIGHT, text = group,
                                font = self.bigFont)
        
        for i in range(len(self.systems)):
            x0 = TopLevelView.ROD_BOX_START_X
            y0 = (TopLevelView.ROD_BOX_START_Y +
                 (i * (TopLevelView.ROD_BOX_HEIGHT +
                       TopLevelView.ROD_BOX_VERTICAL_OFFSET)))
            x1 = x0 + TopLevelView.ROD_BOX_WIDTH
            y1 = y0 + TopLevelView.ROD_BOX_HEIGHT
            
            box = Box(group, self.systems[i], self.canvas)
            box.create(x0, y0, x1, y1, state.color)
            box.text(x0 + TopLevelView.TEXT_LABEL_OFFSET,
                          y0 + TopLevelView.ROD_BOX_HEIGHT / 2,
                          self.systems[i], self.boxTitleFont)
            self.compStore.append(box)
            
    
    def __createRosBoxes(self):
        state = Inactive()
        group = "ROS" # title
        self.canvas.create_text(TopLevelView.ROS_BOX_START_X +
                                TopLevelView.TEXT_LABEL_OFFSET,
                                TopLevelView.ROS_BOX_START_Y -
                                TopLevelView.ROD_BOX_HEIGHT,
                                text = group, font = self.bigFont)

        for i in range(len(self.systems)):
            # need to get a tree node controlling the created component
            try:
                rosTree = self.app.rosTrees[self.systems[i]]
                node = rosTree.root
                box = RenderableBox(group, self.canvas, node)
            except KeyError:
                # some defined system don't have data (node) to be controlled by
                box = Box(group, self.systems[i], self.canvas)
                
            x0 = TopLevelView.ROS_BOX_START_X
            y0 = (TopLevelView.ROS_BOX_START_Y +
                 (i * (TopLevelView.ROD_BOX_HEIGHT +
                 TopLevelView.ROD_BOX_VERTICAL_OFFSET))) 
            x1 = x0 + TopLevelView.ROD_BOX_WIDTH
            y1 = y0 + TopLevelView.ROD_BOX_HEIGHT
            
            idBox = box.create(x0, y0, x1, y1, state.color)
            idText = box.text(x0 + TopLevelView.TEXT_LABEL_OFFSET,
                              y0 + TopLevelView.ROD_BOX_HEIGHT / 2,
                              self.systems[i], self.boxTitleFont)
            dch = DoubleClickHandler(box, self)
            # bind both IDs - box and text in the box
            self.canvas.tag_bind(idBox, "<Double-1>", dch)
            self.canvas.tag_bind(idText, "<Double-1>", dch)
            
            self.compStore.append(box)
            
            
    def __createRodRosLines(self):
        group = "RODROSLINE"
        for i in range(len(self.systems)):
            x0 = TopLevelView.ROD_BOX_START_X + TopLevelView.ROD_BOX_WIDTH 
            y0 = (TopLevelView.ROS_BOX_START_Y +
                 (i * (TopLevelView.ROD_BOX_HEIGHT + TopLevelView.ROD_BOX_VERTICAL_OFFSET)) +
                 TopLevelView.ROD_BOX_HEIGHT / 2)
            x1 = TopLevelView.ROS_BOX_START_X
            y1 = y0
            
            line = Line(group, self.systems[i], self.canvas)
            line.create(x0, y0, x1, y1)
            self.compStore.append(line)
