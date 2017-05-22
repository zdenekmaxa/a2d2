"""
Testing script for communication with the TDAQ IS.
Needs to have TDAQ release set up beforehand.
Mode documentation on ispy package usage in the TDAQ
release where this Python package for communication
with TDAQ IS (C++/CORBA) is distributed.

"""

import re
from ispy import IPCPartition
from ispy import InfoReader

partition = IPCPartition("ATLAS")

readerDfm = InfoReader(partition, "DF", ".*DFM.*")
readerDfm.update()

readerRos = InfoReader(partition, "DF", ".*" + "DataChannel.*")
readerRos.update()

dfm = readerDfm.objects["DF.DFM-1"]

# example of ROS/ROB key (object name):
# 'DF.ROS.ROS-TIL-LBC-01.DataChannel0'
print readerRos.objects

print dfm
print type(dfm)

print  dfm.__getattribute__("SFI non busy messages")
