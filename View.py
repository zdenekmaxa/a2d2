"""
Generic view implementation.

RenderableBox are used for drawing of components which have
representation in the data tree, unlike some components in the
TopLevelView (thus only RenderableBox and no Box class is used here).

"""


from Tkinter import Toplevel
from Tkinter import Canvas
from Tkinter import YES
from Tkinter import BOTH
from Tkinter import RIGHT
from Tkinter import LEFT
from Tkinter import Y
from Tkinter import Scrollbar
import tkMessageBox

from Config import Config as conf
from BaseView import BaseView
from BaseView import DoubleClickHandler
from BaseView import RenderableBox



class View(BaseView):
    
    TEXT_LABEL_OFFSET = 50
    BOX_START_X = 30 
    BOX_START_Y = 45
    BOX_WIDTH = 100
    BOX_HEIGHT = 45
    BOX_VERTICAL_OFFSET = 15
    
    ANOTHER_GUI_OFF = 30
    GUI_WIDTH = 170
    

    def __init__(self, tkRoot, app, masterComp, parentNode, logger):
        BaseView.__init__(self, tkRoot, app, logger)
        # master (upper level view) component on which this view was issued
        self.masterComp = masterComp
        
        self.parentNode = parentNode
                    
        # open detailed window - will go into View class, create Canvas in this window         
        self.window = Toplevel(self.tkRoot)

        # self.window.bind("<<close-window>>", self.__onClose) # doesn't work
        self.window.protocol("WM_DELETE_WINDOW", self.__onClose)
        self.window.title("%s" % self.masterComp.name)
        
        self.canvas = Canvas(self.window, bg = BaseView.CANVAS_BG_COLOR)
        self.canvas.pack(expand = YES, fill = BOTH)
        
        self.app.addActiveView(self.masterComp.name, self)
        
        
    def createContent(self):
        self.__setWindowGeometry()
        self.__setScrollableView()
        self.__createBoxes()
        
        
    def __setScrollableView(self):
        """Sets a scrollbar and scroll area corresponding to number of
           boxes the views needs to accommodate.
        """
        oneBoxSpace = View.BOX_HEIGHT + View.BOX_VERTICAL_OFFSET
        vertNeeded = len(self.parentNode.children) * oneBoxSpace + View.BOX_START_Y
        if (View.BOX_START_Y + vertNeeded) <  conf.GUI_HEIGHT:
            return
        
        self.logger.debug("View needs to be scrollable, setting ...")
        self._setScrollBar(vertNeeded)
        

    def _setScrollBar(self, verticalSpace):
        """Derived class RosView calls this method."""
        self.canvas.config(scrollregion = (0, 0, 200, verticalSpace))
        self.canvas.config(highlightthickness = 0) # no pixels to border
        
        sbar = Scrollbar(self.canvas)
        sbar.config(command = self.canvas.yview)          # xlink sbar and canv
        self.canvas.config(yscrollcommand = sbar.set)     # move one moves other
        sbar.pack(side = RIGHT, fill = Y)                 # pack first=clip last
        self.canvas.pack(side = LEFT, expand = YES, fill = BOTH) # canvas clipped first
                
        
    def __createBoxes(self):
        # always be the same as self.masterComp.name (title and label must agree)
        group = self.parentNode.name # self.masterComp.name
                     
        self.canvas.create_text(View.BOX_START_X + View.TEXT_LABEL_OFFSET,
                                View.BOX_START_Y - View.BOX_VERTICAL_OFFSET,
                                text = group, font = self.bigFont)
        
        nodeKeys = self.parentNode.children.keys()
        nodeKeys.sort() # sort the keys alphabetically
        for i in range(len(nodeKeys)):
            node = self.parentNode.children[nodeKeys[i]]
            x0 = View.BOX_START_X
            y0 = (View.BOX_START_Y +
                 (i * (View.BOX_HEIGHT + View.BOX_VERTICAL_OFFSET)))
            x1 = x0 + View.BOX_WIDTH
            y1 = y0 + View.BOX_HEIGHT
            
            box = RenderableBox(self.masterComp.name, self.canvas, node)          
            dch = DoubleClickHandler(box, self)
            idBox = box.create(x0, y0, x1, y1, node.state.color)
            idText = box.text(x0 + View.TEXT_LABEL_OFFSET,
                              y0 + View.BOX_HEIGHT / 2,
                              node.name, self.boxTitleFont)
            # bind both IDs - box and text in the box
            self.canvas.tag_bind(idBox, "<Double-1>", dch)
            self.canvas.tag_bind(idText, "<Double-1>", dch)
            
            # could even perhaps be list and not a dictionary
            self.compStore.append(box)
            
    
    def openDetailedView(self, comp):
        # check if view which is to be open has not been opened already
        if self.app.isViewActive(comp.name):
            m = ("View '%s' is already among active windows, "
                "not created." % comp.name)
            self.logger.warn(m)
            tkMessageBox.showwarning("Quit", m, parent = self.window)
            return

        try:
            rootNode = self.parentNode.children[comp.name]
        except KeyError:
            self.logger.error("Could not access child node for '%s'" % comp.name)
        else:
            V = rootNode.viewerForChildren
            v = V(self.tkRoot, self.app, comp, rootNode, self.logger)
            v.createContent()
            self.logger.debug("View created: name '%s' root node: "
                              "'%s'" % (comp.name, rootNode.name))
                
                    
    def __onClose(self):
        self.app.removeActiveView(self.masterComp.name)
        self.window.destroy()
        
        
    def __setWindowGeometry(self):
        offsetX = View.ANOTHER_GUI_OFF * self.app.activeViewsCount()
        x = conf.GUI_OFF_X + conf.GUI_WIDTH + offsetX
        geom = "%sx%s+%s+%s" % (View.GUI_WIDTH, conf.GUI_HEIGHT, x, conf.GUI_OFF_Y)
        self.window.geometry(geom)
