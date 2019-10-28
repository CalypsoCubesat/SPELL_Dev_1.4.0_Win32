###################################################################################
## MODULE     : interface.model
## DATE       : Mar 18, 2011
## PROJECT    : SPELL
## DESCRIPTION: Fuzzer data model
## -------------------------------------------------------------------------------- 
##
##  Copyright (C) 2008, 2015 SES ENGINEERING, Luxembourg S.A.R.L.
##
##  This file is part of SPELL.
##
## This component is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SPELL. If not, see <http://www.gnu.org/licenses/>.
##
###################################################################################

#*******************************************************************************
# SPELL imports
#*******************************************************************************
from spell.lib.adapter.config import Configurable
from spell.lib.exception import *
from spell.lang.constants import *
from spell.lang.modifiers import *

#*******************************************************************************
# Local imports
#*******************************************************************************
from tm_sim_item import *
from tc_sim_item import *
from lazypy import delay
from spell.lib.registry import REGISTRY
#*******************************************************************************
# System imports
#*******************************************************************************
import time
import sys
import cPickle as pickle

#*******************************************************************************
# Import definition
#*******************************************************************************
__all__ = ['SimulatorModel']

#*******************************************************************************
# Module globals
#*******************************************************************************
TM_PREFIX = "-TM-"
TC_PREFIX = "-TC-"

################################################################################
class SimulatorModel(Configurable):

    tmClass = None
    tcClass = None
    tmItems = {}
    tcItems = {}
    gpItems = {}
    cfgItems = {}

    rh = None
    ctxId = None

    #===========================================================================    
    def __init__(self):
        Configurable.__init__(self)
        self.tmClass = None
        self.tcClass = None
        self.tmItems = {}
        self.tcItems = {}
        self.gpItems = {}
        self.cfgItems = {}

    #===========================================================================    
    def setup(self, ctxId, defFile = None):
        self.ctxId = ctxId
        # Connect to Redis
        #self.rh = redis.StrictRedis(host='localhost', port=6379, db=0)

    #===========================================================================    
    def cleanup(self):
        return

    #===========================================================================    
    def executeCommand(self, tcItem):
        # TODO
        print 'Command ' + str(tcItem.name()) + ' received'
        params = tcItem._getParams()
        if params:
            print("    Arguments:")
            for param in params:
                print("        " + str(param.name) + " = " + str(param.value.get()))
        return

    #===========================================================================    
    def changeTMitem(self, tmItem, value):
        #tmItem = self.getTMitem(tmItemName)
        try:
            tmItem._setRaw( int(value) )
        except:
            tmItem._setRaw( value )
            
        return True

    #===========================================================================    
    def changeGPitem(self, gpItem, value):
        #gpItem = self.getGPitem(gpItemName)
        try:
            gpItem._setRaw( int(value) )
        except:
            gpItem._setRaw( value )

    #===========================================================================    
    def changeCFGitem(self, cfgItemName, value):
        self.getCFGitem(cfgItemName)
        self.tmItems[cfgItemName] = value
        return True

    #===========================================================================    
    def getTMitem(self, name):
        tmItem = None
        #name = self.ctxId + TM_PREFIX + name
        if self.tmItems.has_key(name):
            tmItem = self.tmItems[name]
        else:
            tmItem = TmItemSimClass(self,name,'')
            self.tmItems[name] = tmItem
        # TODO
        #tmItem.update()
        return tmItem

    #===========================================================================    
    def isGPitem(self, name):
        return self.tmItems.has_key(name)

    #===========================================================================    
    def getGPitem(self, name):
        if not self.tmItems.has_key(name):
            gpItem = TmItemSimClass(self,name,'')
            self.tmItems[name] = gpItem
        else:
            gpItem = self.tmItems[name]
        return gpItem

    #===========================================================================    
    def getTCitem(self, name):
        if self.tcItems.has_key(name):
            return self.tcItems[name]
        else:
            tcItem = TcItemSimClass(self, name)
            self.tcItems[name] = tcItem
            return tcItem

    #===========================================================================    
    def getCFGitem(self, name):
        if not self.cfgItems.has_key(name):
            # TODO
            cfgItemValue = delay(REGISTRY['CIF'].prompt,('Please select the value for global ' + str(name),{},{'Type':0}))
            
            #raise DriverException("Unknown GCS configuration parameter: " + repr(name))
        else:
            cfgItemValue = self.cfgItems[name]
        return cfgItemValue
