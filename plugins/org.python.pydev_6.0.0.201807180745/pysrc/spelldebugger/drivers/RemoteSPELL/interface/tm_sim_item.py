###################################################################################
## MODULE     : interface.tm_sim_item
## DATE       : Mar 18, 2011
## PROJECT    : SPELL
## DESCRIPTION: TM item for the simulation model
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
from spell.lib.adapter.tm_item import TmItemClass
from spell.lib.registry import REGISTRY
#*******************************************************************************
# Local imports
#*******************************************************************************
from lazypy import delay
#*******************************************************************************
# System imports
#*******************************************************************************
import os
import random
import inspect
import urllib2
TM_PREFIX = "-TM-"
TC_PREFIX = "-TC-"
#*******************************************************************************
# Import definition
#*******************************************************************************
__all__ = ['TmItemSimClass']

#*******************************************************************************
# Module globals
#*******************************************************************************

################################################################################
def getSourceText(source_file,line):
    fo = None
    try :
        line -= 1
        #print source_file + ':' + str(line)
        fo = open(source_file,'r')
        lines = fo.readlines()
        hint = '    ' + lines[line].strip() + '\n    ...\n'
        return '\nSource Hint:\n' + hint
    except:
        pass
    finally:
        if fo:
            fo.close()
    return ''
def getCurrentSourceText(prevSrcText):
    fo = None
    try :
        source_file = inspect.stack()[5][1]
        line = inspect.stack()[5][2]
        
        line -= 1
        #print 'current: ' + source_file + ':' + str(line)
        fo = open(source_file,'r')
        lines = fo.readlines()
        hint = ' -->' + lines[line].strip()
        return prevSrcText + hint
    except:
        pass
    finally:
        if fo:
            fo.close()
    return ''

def PromptWithCurrentText(text,opt,config):
    currentHint = getCurrentSourceText(text)

    return REGISTRY['CIF'].prompt(currentHint,opt,config)
    
class TmItemSimClass(TmItemClass):
    
    # ==========================================================================    
    def __init__(self, model, name, description,proxy=False):
        TmItemClass.__init__(self, model.tmClass, name, description)
        self._proxyName = name
        if not proxy:
            from pydevd import SetupHolder
            if SetupHolder.setup:
                tmtc_Server = SetupHolder.setup['tmtc-db-server']
            else:
                tmtc_Server = None
            if not tmtc_Server:
                self.tm_data = None
                return
            try:
                req = urllib2.Request(url=tmtc_Server + TM_PREFIX + name)
                tm_answer = urllib2.urlopen(req)
                self.tm_data = eval(tm_answer.read(),{'null':None},{'null':None})
            except:
                print 'Failed to load data for TM ' + name
                self.tm_data = None
            #ENDTRY

        #ENDIF
        # set initial value
        #self.prepareValues()
        # set random seed
        seed = os.getenv("SPELL_RANDOM_SEED")
        if seed:
            random.seed(seed)
    def proxyName(self):
        return self._proxyName
    def name(self):
        return REGISTRY['REMOTE']._TM_name(self)
    def value(self):
        return REGISTRY['REMOTE']._TM_value(self)
    def time(self):
        return REGISTRY['REMOTE']._TM_time(self)
    def description(self):
        return REGISTRY['REMOTE']._TM_description(self)
    def eng(self):
        return REGISTRY['REMOTE']._TM_eng(self)
    def fullName(self):
        return REGISTRY['REMOTE']._TM_fullName(self)
    def raw(self):
        return REGISTRY['REMOTE']._TM_raw(self)
    def status(self):
        return REGISTRY['REMOTE']._TM_status(self)
    def refresh(self):
        return REGISTRY['REMOTE']._TM_refresh(self)
        
    #==========================================================================    
    def __str__(self):
        return "[TM=" + repr(self.proxyName()) + "]" 
    
    __repr__ = __str__
################################################################################
