"""
Comprises of several ROB (DataChannel object) grouped by three.

"""

import tkMessageBox

from Config import Config as conf
from View import View
from BaseView import DoubleClickHandler
from BaseView import RenderableBox


class RosView(View):
    
    NUM_COLUMNS = 3
    LABEL_Y = 18
    GUI_WIDTH = 400
    GUI_HEIGHT = 400
    BOX_HORIZONTAL_OFFSET = 15
    
    
    def __init__(self, tkRoot, app, masterComp, parentNode, logger):
        View.__init__(self, tkRoot, app, masterComp, parentNode, logger)


    def createContent(self):
        self.__setWindowGeometry()
        self.__setScrollableView()
        self.__createBoxes()

        
    def __setScrollableView(self):
        oneRow = View.BOX_HEIGHT + View.BOX_VERTICAL_OFFSET
        numRows = len(self.parentNode.children) / RosView.NUM_COLUMNS 
        vertNeeded = numRows * oneRow + View.BOX_START_Y
        if (View.BOX_START_Y + vertNeeded) <  RosView.GUI_HEIGHT:
            return
        
        self.logger.debug("View needs to be scrollable, setting ...")
        self._setScrollBar(vertNeeded)
        

    def __setWindowGeometry(self):
        offsetX = View.ANOTHER_GUI_OFF * self.app.activeViewsCount()
        x = conf.GUI_OFF_X + conf.GUI_WIDTH + offsetX
        geom = "%sx%s+%s+%s" % (RosView.GUI_WIDTH, RosView.GUI_HEIGHT, 
                                x, conf.GUI_OFF_Y)
        self.window.geometry(geom)
        
        
    def __createBoxes(self):
        # always be the same as self.masterComp.name (title and label must agree)
        group = self.parentNode.name # self.masterComp.name
        
        self.canvas.create_text(RosView.GUI_WIDTH / 2, RosView.LABEL_Y,
                                text = group, font = self.bigFont)
        
        # ROBs which constitute this ROS view are named DataChannel1 - DataChannelX
        # sorting alphabetically doesn't quite work since 0, 1, 10, 2, 3 ... (damn!)
        numRobs = len(self.parentNode.children)
        nodeKeys = []
        for i in range(numRobs):
            key = "".join(["DataChannel", str(i)])
            try:
                self.parentNode.children[key]
                nodeKeys.append(key)
            except KeyError:
                m = "Creating RosView: key '%s' doesn't exist, fatal." % key
                self.logger.fatal(m)
                tkMessageBox.showerror("Quit", m, parent = self.window)
                return
        
        count, rows = 0, 0
        for i in range(len(nodeKeys)):
            node = self.parentNode.children[nodeKeys[i]]
            x0 = (View.BOX_START_X +
                 (count * (View.BOX_WIDTH + RosView.BOX_HORIZONTAL_OFFSET))) 
            y0 = (View.BOX_START_Y +
                 (rows * (View.BOX_HEIGHT + View.BOX_VERTICAL_OFFSET)))
            x1 = x0 + View.BOX_WIDTH
            y1 = y0 + View.BOX_HEIGHT
            
            box = RenderableBox(self.masterComp.name, self.canvas, node)
            idBox = box.create(x0, y0, x1, y1, node.state.color)
            idText = box.text(x0 + View.TEXT_LABEL_OFFSET,
                              y0 + View.BOX_HEIGHT / 2,
                              node.name, self.smallerBoxTitleFont)
            # bind both IDs - box and text in the box
            dch = DoubleClickHandler(box, self)
            self.canvas.tag_bind(idBox, "<Double-1>", dch)
            self.canvas.tag_bind(idText, "<Double-1>", dch)
            self.compStore.append(box)
            
            count += 1
            if count % RosView.NUM_COLUMNS == 0: # 3 ROBs in a row
                count = 0
                rows += 1
