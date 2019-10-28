###################################################################################
## MODULE     : interface.tc_sim_item
## DATE       : Mar 18, 2011
## PROJECT    : SPELL
## DESCRIPTION: TC item for simulated model
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
from spell.lib.adapter.tc_item import TcItemClass

#*******************************************************************************
# Local imports
#*******************************************************************************
import urllib2
TM_PREFIX = "-TM-"
TC_PREFIX = "-TC-"
#*******************************************************************************
# System imports
#*******************************************************************************

#*******************************************************************************
# Import definition
#*******************************************************************************
__all__ = ['TcItemSimClass']

#*******************************************************************************
# Module globals
#*******************************************************************************

################################################################################
class TcItemSimClass(TcItemClass):

    ccfItem = None

    #==========================================================================    
    def __init__(self, model, name, description='', ccfItem=None,proxy=False):
        TcItemClass.__init__(self, model.tcClass, name, description)
        if not proxy:
            from pydevd import SetupHolder
            tmtc_Server = SetupHolder.setup['tmtc-db-server']
            if SetupHolder.setup:
                tmtc_Server = SetupHolder.setup['tmtc-db-server']
            else:
                tmtc_Server = None
            if tmtc_Server:
                req = urllib2.Request(url=tmtc_Server + TC_PREFIX + name)
                try:
                    tc_answer = urllib2.urlopen(req)
                    self.tc_data = eval(tc_answer.read(),{'null':None},{'null':None})
                except:
                    print 'Failed to load data for TC ' + name
                    self.tc_data = None
                #ENDTRY
            #ENDIF
        #ENDIF
    #==========================================================================
    def __str__(self):
        return "[TC=" + repr(self.name()) + ", DESC=" + repr(self.desc()) + "]"    

################################################################################
class PtcItemSimClass(TcItemClass):

    ccfItem = None

    #==========================================================================    
    def __init__(self, model, name, description='', ccfItem=None,proxy=False):
        TcItemClass.__init__(self, model.tcClass, name, description)
       
    #==========================================================================
    def __str__(self):
        return "[PTC=" + repr(self.name()) + ", DESC=" + repr(self.desc()) + "]"    
