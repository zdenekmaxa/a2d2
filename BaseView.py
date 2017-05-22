"""
Base class of Views with canvas.
Classes for Canvas primitives (Box, RenderableBox, Line, etc)

"""

import tkFont
from Tkinter import LAST



class DoubleClickHandler(object):
    def __init__(self, component, view):
        self.component = component
        self.view = view


    def __call__(self, event):
        self.view.logger.debug("Double click on: %s" % self.component)
        self.view.openDetailedView(self.component)
  
        

class BaseView(object):
    CANVAS_BG_COLOR = "#DDDDDD"
        
    def __init__(self, tkRoot, app, logger):
        self.tkRoot = tkRoot
        self.app = app # reference to the main application
        self.logger = logger

        # must be initialised after Tkinter root object exits, otherwise
        # fails in tkFont.Font()
        # problems when fonts were static variables ... working all right
        # when instance variables ... (not properly understood though)
        self.boxTitleFont = tkFont.Font(family="Helvetica", size = 9,
                                        weight = "bold")
        self.bigFont = tkFont.Font(family="Helvetica", size = 14, weight = "bold")
        self.smallerBoxTitleFont = tkFont.Font(family="Helvetica", size = 9)

        # due to thread safety problems ... Application.__onClose()
        # and concurrent view updates run from ThreadChecker ...
        # if set, no component updating happens (prevents from hanging ...)        
        self.__stopUpdating = False
        
        # canvas component (box, etc) store
        self.compStore = []
        

    def stopUpdating(self):
        # adding lock around made no difference, see further comment in
        # the main file
        self.__stopUpdating = True

        
    def updateView(self):
        for comp in self.compStore:
            if self.__stopUpdating:
                self.logger.warn("BaseView.updateView(): stopUpdating flag "
                                 "True, quit updating.")
                break
            else:
                # time.sleep(5) makes it hang at closing (thread-safety problem)
                comp.render()
                    


class Component(object):
    def __init__(self, group, name, canvas):
        self.group = group   # "ROD" or "ROS" (group) or further separation
        self.name = name     # "LAR" or "TIL", etc (name of the particular comp.)
        self.canvas = canvas
        self.color = None
        self.ids = [] # list of associated canvas IDs
        
        
    def __str__(self):
        return ("component group: '%s' ids: '%s' name: '%s' color: '%s'" 
                % (self.group, self.ids, self.name, self.color)) 

                
    def render(self):
        pass

        

class Box(Component):
    def __init__(self, group, name, canvas):
        Component.__init__(self, group, name, canvas)
        self.controlNode = None
            
        
    def create(self, x0, y0, x1, y1, color):
        self.color = color
        id = self.canvas.create_rectangle(x0, y0, x1, y1, width = 1,
                                          fill = self.color)
        self.ids.append(id)
        return id

    
    def text(self, x0, y0, text, font):
        # should also have text title color?
        id = self.canvas.create_text(x0, y0, text = text, font = font)
        self.ids.append(id)
        return id
                        


class RenderableBox(Box):
    def __init__(self, group, canvas, node):
        Box.__init__(self, group, node.name, canvas)
        self.controlNode = node

        
    def render(self):
        try:
            id = self.ids[0] # just paranoid check
        except IndexError:
            print "Could not get first subcomponent id at %s" % self
        else:
            # can be used to configure objects on the canvas
            # first id is always the box, second is the title
            self.canvas.itemconfig(id, fill = self.controlNode.state.color)
            
        

class Line(Component):
    """
    ... will change color, react to change of some conditions / criteria.
    
    """
    def __init__(self, group, name, canvas):
        Component.__init__(self, group, name, canvas)
            
    
    def create(self, x0, y0, x1, y1):
        id = self.canvas.create_line(x0, y0, x1, y1, width = 1, arrow = LAST)
        self.ids.append(id)
        return id
