from common.States import Error
from common.States import Alert
from common.States import Ok
from common.States import Inactive


class Criteria(object):
    def __init__(self, condition, state):
        # if condition is fulfilled (True), then result of
        # this criteria checking is this state attribute
        self.condition = condition
        self.state = state

        
class RosCriteriaConfig(object):
    def __init__(self):
        # values from DataFlowManager
        self.objectKeyDfm = "DF.DFM-1"
        self.valueKeyDfmClearedEvents = "cleared events"

        # just names of values to get (retrieve - parse from DF objects)
        self.valueKeysDf = [ "rolXoffStat",
                             "bufferFull",
                             "rolDownStat",
                             "pagesInUse",
                             "pagesFree",
                             "fragstruncated",
                             "fragsreceived",
                             "fragscorrupted",
                             "fragsreceived",
                             "lastl1id",
                             "mostRecentId",
                             "numberOfNotDeleted" ]
        
        # criteria which have result state Error have higher priority than
        # those with lower priority result state if the condition is fulfilled
        self.criteria = [
            Criteria("%(rolXoffStat)s == 1", Error()),
            Criteria("%(bufferFull)s == 1", Error()),
            Criteria("%(rolDownStat)s == 1", Error()),
            Criteria("abs(%(lastl1id)s - %(mostRecentId)s) > 33554432", Error()),
            Criteria("%(numberOfNotDeleted)s > 0.9 * %(cleared events)s", Error()),            
            Criteria("0.2 * %(pagesInUse)s > %(pagesFree)s", Alert()),
            Criteria("%(fragstruncated)s > 0.1 * %(fragsreceived)s", Alert()),
            Criteria("%(fragscorrupted)s > 0.1 * %(fragsreceived)s", Alert()),
            Criteria("%(numberOfNotDeleted)s > 0.5 * %(cleared events)s", Alert())
        ]

   
        
"""
example of DF.DFM-1 (DataFlowManager) IS object):
        
NAME : DF.DFM-1
TYPE : DFM
TIME : 1/7/09 15:14:13.457567
Averaging time for rates : 10.026095
LVL2 accepts : 285957
LVL2 rejects : 33509048
Number of disabled SFIs : 0
Rate of LVL2 accepts : 84.5792903419
Rate of LVL2 rejects : 10188.6128149
Rate of assigned events : 84.679030071
Rate of built events : 84.679030071
Rate of cleared events : 10273.2918449
SFI busy messages : 0
SFI non busy messages : 13960
assigned events : 285913
built events : 285913
cleared events : 33794961
current XOFF : 0
event duplication warnings : 0
failed assignments : 0
input queue : 0
latest GID : 285912
latest L1ID : 2902499429
number of XOFF : 0
reasked events : 0
timeout events : 0
unknown L1ID in EoE : 0


example of DF (ROS -> ROB DataChannel) object, key to this object would be
"DF.ROS.ROS-TIL-LBC-01.DataChannel0":
NAME : DF.ROS.ROS-TIL-LBC-01.DataChannel0
TYPE : RobinDataChannelInfo
TIME : 1/7/09 15:14:09.420236
bufferFull : 0
fragscorrupted : 0
fragsreceived : 33805389
fragstruncated : 0
gcAvDeleted : 0
gcAvFree : 0
gcBad : 0
gcOK : 0
lastl1id : 2919242474
lastmsg : 2
level1RateHz : 10287
mostRecentId : 2919243115
numberOfMayCome : 0
numberOfNeverToCome : 0
numberOfNotDeleted : 0
pagesFree : 7700
pagesInUse : 491
robId : 8
rolDownStat : 0
rolXoffStat : 0
statusErrors : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

"""
