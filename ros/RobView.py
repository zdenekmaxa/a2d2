"""
Detailed DataChannel (ROB). List of criteria and their results.
Could be done in nicer (coloured) graphical representation.

"""

from Tkinter import DISABLED
from Tkinter import LEFT
from Tkinter import RIGHT
from Tkinter import Y
from Tkinter import Toplevel
from Tkinter import Scrollbar
from Tkinter import Text
from Tkinter import END
from ScrolledText import ScrolledText


from Config import Config as conf
from BaseView import BaseView
from View import View



class RobView(View):
    GUI_WIDTH = 800
    GUI_HEIGHT = 400
    
    def __init__(self, tkRoot, app, masterComp, parentNode, logger):
        BaseView.__init__(self, tkRoot, app, logger)
        # master (upper level view) component on which this view was issued
        self.masterComp = masterComp
        
        self.parentNode = parentNode
                             
        self.window = Toplevel(self.tkRoot)
        self.window.title("%s" % parentNode.keyForIsObject)
        
        # self.window.bind("<<close-window>>", self.__onClose) # doesn't work
        self.window.protocol("WM_DELETE_WINDOW", self.__onClose)
        
        text = ScrolledText(self.window, width = RobView.GUI_WIDTH,
                            height = RobView.GUI_HEIGHT, background='white')
        text.pack(fill = Y)
        
        # information from ROB (DataChannel) IS object (criteria results)
        # .valueOfIsObject is a bit misleading since it's criteria results
        # checks based on particular values (attributes) within the IS object
        m = ("ROB '%s':\n\n%s" %
             (parentNode.keyForIsObject, parentNode.valueOfIsObject))
        text.insert(END, m)
        
        text.configure(state = DISABLED) # disable edit now, not before insert
        
        # need to store this view under full name (not only under 
        # self.masterComp.name as the other views), since there may be 
        # a number of views named e.g. 'DataChannel0'
        self.app.addActiveView(self.parentNode.keyForIsObject, self)

        
    def createContent(self):
        self.__setWindowGeometry()
        
        
    def __setWindowGeometry(self):
        offsetX = View.ANOTHER_GUI_OFF * self.app.activeViewsCount()
        x = conf.GUI_OFF_X + conf.GUI_WIDTH + offsetX
        geom = "%sx%s+%s+%s" % (RobView.GUI_WIDTH, RobView.GUI_HEIGHT, 
                                x, conf.GUI_OFF_Y)
        self.window.geometry(geom)

        
    def __onClose(self):
        self.app.removeActiveView(self.parentNode.keyForIsObject)
        self.window.destroy()
