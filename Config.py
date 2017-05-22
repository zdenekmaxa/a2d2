"""
Module holding configuration values.

__author__ = Zdenek Maxa

"""

import sys
import logging


class Config(object):
    """
    Class holding configuration values (as static class attributes)
    
    """
    
    # following directories must be available in sys.path in order to load
    # modules from (done below)
    APPLICATION_DIR = ""
    
    # Subsystems names (e.g. main ROD / ROS element names)
    
    
    PATH_DIRS = [APPLICATION_DIR,
                 "/usr/local/lib/python2.5/site-packages"]
        
    APPLICATION_LOG_FILE = "/tmp/r2d2.log"
        
    # default logging level
    LOGGING_LEVEL = logging.DEBUG
    
    # operation mode (options 'prod', 'production', 'devel', 'development')
    MODE = "production"
    
    # IS server partition to query on. Different partition could be provided
    # as command line argument 
    DEFAULT_PARTITION = "ATLAS"
    
    # names of the subsystems
    SYSTEMS = ("L1CTP", "L1CAL", "L1MU", "BCM", "PIX", "SCT", "TRT", "LAR",
               "TIL", "MDT", "RPC", "TGC", "CSC", "LUC", "ZDC")

    # ROS IS objects names patterns - 1st, 2nd, 3rd level patterns
    # this may of course change in future resulting in not finding
    # object names which are supposed to be found and checked by this
    # application ... 
    ROS_IS_NAMES_PATTERNS = ("%(subSystem)s-[A-Z]*\d*",
                             "%(subSystem)s-[A-Z]*\d*-[A-Z]*\d*",
                             "DataChannel.*")
    
    # window geometry, these parameters used as e.g. "400x600+400+300"
    GUI_WIDTH = 400
    GUI_HEIGHT = 600
    GUI_OFF_X = 150
    GUI_OFF_Y = 300
    


for pathDir in Config.PATH_DIRS:
    if pathDir not in sys.path:
        sys.path.append(pathDir)
