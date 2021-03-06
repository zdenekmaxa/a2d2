"""
Metaclass implementation of State classes (class names as defined in
'classNames'.
Class is generated by calling type() - could also instantiate a 'MetaClass'
which would from its __new__() method return the same thing - class as
result of a type() call.
Much shorter solution - rather than defining 4 times the same class with
different values at attributes (values correspond to nameSpace).

"""

import sys


class BaseState(object):
    def __str__(self):
        return "'%s' (code %s)" % (self.name, self.code)
    
    def __cmp__(self, other):
        if self.code < other.code: return -1
        if self.code == other.code: return 0
        if self.code > other.code: return 1
     
"""
class Error(BaseState):
    def __init__(self):
        self.color = "#FF0000" # red
        self.code = 4 # weight of the state (priority)
        self.name = "Error"
        
    
class Alert(BaseState):
    def __init__(self):
        self.color = "#FF9933" # orange
        self.code = 3
        self.name = "Alert"
        
                
class Ok(BaseState):
    def __init__(self):
        self.color = "#33CC00" # green
        self.code = 2
        self.name = "OK"
                
        
class Inactive(BaseState):
    def __init__(self):
        self.color = "#ABABAB" # grey
        self.code = 1
        self.name = "Inactive"

             
class NotAssociated(BaseState):
    def __init__(self):
        self.color = "#FFFFFF" # white
        self.code = 0
        self.name = "Not associated"
        
        

# code - weight of the state (priority) (if something is in state Alert,
#    another sub-condition evaluated as Ok doesn't change this state
#    whereas Error state does)
# Inactive - Rules (criteria) in the application exists, but not sure if
#     present in the ATLAS partition.
# NotAssociated - Rules (criteria) in the application doen't exists for
#    this component, not associated with monitoring in the application.

"""


classNames = ("Error", "Alert", "Ok", "Inactive", "NotAssociated")
nameSpace = ("color", "code", "name")
values = ( ("#FF0000", 4, "Error"),         # red
           ("#FF9933", 3, "Alert"),         # orange
           ("#33CC00", 2, "OK"),            # green
           ("#ABABAB", 1, "Inactive"),      # grey
           ("#FFFFFF", 0, "Not associated") # white
         )

for className, attribs in zip(classNames, values):
    ns = {}
    for name, value in zip(nameSpace, attribs): ns[name] = value
    newClass = type(className, (BaseState,), ns) # metaclass
    setattr(sys.modules[__name__], className, newClass)    
