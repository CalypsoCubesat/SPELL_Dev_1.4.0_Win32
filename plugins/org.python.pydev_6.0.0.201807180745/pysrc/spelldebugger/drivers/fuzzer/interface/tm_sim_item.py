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

def PromptNumWithCurrentText(text,opt,config):
    currentHint = getCurrentSourceText(text)

    return int(REGISTRY['CIF'].prompt(currentHint,opt,config))

def PromptWithCurrentText(text,opt,config):
    currentHint = getCurrentSourceText(text)

    return eval(REGISTRY['CIF'].prompt(currentHint,opt,config),globals(),locals())
                        
    
class TmItemSimClass(TmItemClass):
    
    pcfItem = None
    ocfItem = None
    ocpItems = None
    txfItem = None
    txpItems = None
    cafItem = None
    capItems = None
    mcfItem = None

    calibratedvalues = None
    monchecks = None

    # ==========================================================================    
    def waitUpdate(self, timeout = None):
        return

    # ==========================================================================    
    def abortUpdate(self):
        return

    def _resetValue(self):
        if  not self.pcfItem:
            if self.tm_data:
                rawCalib = self._extractCalibration('RAW')
                if type(rawCalib) == list:
                    rawValue = int(REGISTRY['CIF'].prompt('Please select the RAW value for TM ' + str(self.name()) ,rawCalib,{'Type':self._extractCalibrationPromptType('RAW')}))
                    engValue = rawValue
                    for calibEntry in rawCalib:
                        if calibEntry.split(':')[0] == str(rawValue):
                            engValue = calibEntry.split(':')[1]
                            break
                        #ENDIF
                    #ENDFOR
                    
                    self._setEng(engValue)
                    self._setRaw(rawValue)
                else:
                    engValue = delay(PromptWithCurrentText,('Please select the ENG value for TM ' + str(self.name()) + getSourceText(inspect.stack()[8][1] ,inspect.stack()[8][2]) if len(inspect.stack()) > 8 else '' ,self._extractCalibration('ENG'),{'Type':self._extractCalibrationPromptType('ENG')}))
                    rawValue = delay(PromptNumWithCurrentText,('Please select the RAW value for TM ' + str(self.name()) + getSourceText(inspect.stack()[8][1],inspect.stack()[8][2]) if len(inspect.stack()) > 8 else '' ,self._extractCalibration('RAW'),{'Type':self._extractCalibrationPromptType('RAW')}))
            
                    self._setEng(engValue)
                    self._setRaw(rawValue)
                #ENDIF
            else:
                engValue = delay(PromptWithCurrentText,('Please select the ENG value for TM ' + str(self.name()) + getSourceText(inspect.stack()[8][1] ,inspect.stack()[8][2]) if len(inspect.stack()) > 8 else '' ,self._extractCalibration('ENG'),{'Type':self._extractCalibrationPromptType('ENG')}))
                rawValue = delay(PromptNumWithCurrentText,('Please select the RAW value for TM ' + str(self.name()) + getSourceText(inspect.stack()[8][1],inspect.stack()[8][2]) if len(inspect.stack()) > 8 else '' ,self._extractCalibration('RAW'),{'Type':self._extractCalibrationPromptType('RAW')}))
        
                self._setEng(engValue)
                self._setRaw(rawValue)
            #ENDIF
    # ==========================================================================    
    def __init__(self, model, name, description):
        TmItemClass.__init__(self, model.tmClass, name, description)
        
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
        
        # set initial value
        #self.prepareValues()
        # set random seed
        seed = os.getenv("SPELL_RANDOM_SEED")
        if seed:
            random.seed(seed)
        
    
    def _extractCalibration(self,valueFormat):
      
        if self.tm_data:
            if type(self.tm_data['calibrations']) == list:
                try:
                    self.tm_data['calibrations'].sort(lambda x,y:x[0] - y[0])
                except:
                    try:
                        self.tm_data['calibrations'].sort(lambda x,y:x[0][0] - y[0][0])
                    except:
                        pass
                #ENDTRY
                possible_Values = []
                for calib in self.tm_data['calibrations']:
                    raw_values = calib[0]
                    eng_values = calib[1]
                    if type(eng_values) != str:
                        #FIXME coeff used for calib?
                        return {}
                    #ENDIF
                    if type(raw_values) == list:
                        raw_values = raw_values[0]
                    #ENDIF
                    if valueFormat == 'RAW':
                        possible_Values += [str(raw_values) + ':' + str(eng_values)]
                    else:
                        possible_Values += [str(eng_values) + ':' + str(raw_values)]
                    #ENDIF
                #ENDFOR
                return possible_Values
            elif type(self.tm_data['calibrations']) == dict:
                possible_Values = []
                print self.tm_data['calibrations']
                for calib in self.tm_data['calibrations'].iteritems():
                    raw_values = calib[0]
                    if '[' in raw_values:
                        raw_values = eval(raw_values)[0]
                    eng_values = calib[1]
                    if type(eng_values) != str:
                        #FIXME coeff used for calib?
                        return {}
                    #ENDIF
                    if type(raw_values) == list:
                        raw_values = raw_values[0]
                    #ENDIF
                    if valueFormat == 'RAW':
                        possible_Values += [str(raw_values) + ':' + str(eng_values)]
                    else:
                        possible_Values += [str(eng_values) + ':' + str(raw_values)]
                    #ENDIF
                #ENDFOR
                return possible_Values
            #ENDIF
        else:
            return {}
    
    def _extractCalibrationPromptType(self,valueFormat):
        if self.tm_data:
            if valueFormat == 'ENG':
                return 96
            else:
                return 96
            #ENDIF
        return 0

    def prepareValues(self):
        if not self.pcfItem:
            return
        name = self.pcfItem.getName()
        paramtype, width = self.pcfItem.getParamType()
        categ = self.pcfItem.getCateg()
        natur = self.pcfItem.getNatur()
        curtx = self.pcfItem.getCurtx()
  
        # no need to prepare other values
        if natur != 'R':
            return

        # Are there monitoring checks available?
        if self.ocfItem != None:
            codin = self.ocfItem.getCodin()
            if codin == 'A':
              res = set()
              for ocpItem in self.ocpItems:
                  # Consider alarms only
                  if ocpItem.getType() != 'A':
                      continue
                  if ocpItem.getLvalu():
                      res.add(ocpItem.getLvalu())
                  if ocpItem.getHvalu():
                      res.add(ocpItem.getHvalu())
              if len(res):
                  self.monchecks = list(res)
            elif codin == 'I' or codin == 'R':
                low, high = None, None
                res = []
                for ocpItem in self.ocpItems:
                    ocpType = ocpItem.getType()
                    # Consider Soft and Hard OOL only
                    if ocpType != 'S' and ocpType != 'H':
                        continue
                    lvalu = ocpItem.getLvalu()
                    hvalu = ocpItem.getHvalu()
                    if len(lvalu):
                      if codin == 'I':
                          res.append(int(lvalu))
                      else:
                          res.append(float(lvalu))
                    if len(hvalu):
                      if codin == 'I':
                          res.append(int(hvalu))
                      else:
                          res.append(float(hvalu))
                res.sort()
                if len(res) == 1:
                    # TODO: does it make sense?
                    self.monchecks = (res[0], res[0])
                elif len(res) > 2:
                    self.monchecks = (res[0], res[len(res)-1])

        # No calibrations
        if curtx == None:
            # sanity checks only
            assert categ == 'N' or categ == 'T', "N or T values only %s %s" % (name, categ)
            if categ == 'T':
                assert paramtype == 'A' and width >= 0, "%s %s" % (name, paramtype)
            else:
                types = ['B', 'R', 'I', 'U', 'O', 'T', 'D']
                assert paramtype in types and width >= 0, "%s %s" % (name, paramtype)
            return

        # Textual calibration
        if categ == 'S':
            res = set()
            assert len(self.txpItems), "txpItems cannot be empty when curtx is set"
            for txpItem in self.txpItems: 
               res.add(txpItem.getAltxt())
            assert len(res), "result cannot be empty"
            self.calibratedvalues = list(res)
            return

        # Numerical calibration
        if categ == 'N':
            res = set()
            assert self.cafItem or self.mcfItem, "capItems/mcfItem cannot be empty when curtx is set"
            if self.cafItem:
                engfmt = self.cafItem.getEngfmt()
                for capItem in self.capItems: 
                    if engfmt == 'I' or engfmt == 'U':
                        res.add(int(capItem.getYvals()))
                    else:
                        res.add(float(capItem.getYvals()))
                assert len(res), "result cannot be empty"
                self.calibratedvalues = list(res)
            else:
                # TODO: do we need to fuzz polynomial values?
                pass
            return

        assert 0, "cannot reach here"

    def update(self):
        if not self.pcfItem:
            self._resetValue()
            return
        name = self.pcfItem.getName()
        paramtype, width = self.pcfItem.getParamType()
        categ = self.pcfItem.getCateg()
        natur = self.pcfItem.getNatur()
        curtx = self.pcfItem.getCurtx()
  
        # No numerical (polynomial) calibrations or other natures than 'N' (synthetic etc.)
        if (categ == 'N' and (curtx == None or self.mcfItem)) or natur != 'R':
            if categ == 'T':
                self._setEng(self.fuzzString(width))
            elif paramtype == 'B':
                self._setEng(self.fuzzBool())
            elif paramtype == 'R':
                self._setEng(self.fuzzReal(width))
            elif paramtype == 'I':
                self._setEng(self.fuzzSignedInt(width))
            elif paramtype == 'U':
                self._setEng(self.fuzzUnsignedInt(width))
            elif paramtype == 'O':
                self._setEng(self.fuzzOctetString(width))
            elif paramtype == 'T':
                self._setEng(self.fuzzAbsoluteTime(width))
            elif paramtype == 'D':
                self._setEng(self.fuzzRelativeTime(width))
            else:
                assert 0, "cannot reach this"
        else:
            assert self.calibratedvalues, "there must be calibrated S/N values for %s" % name
            assert len(self.calibratedvalues), "calibrated S/N values for %s are empty!" % name
            # TODO: include monitoring checks?
            value = self._setEng(random.choice(self.calibratedvalues))

    #==========================================================================    
    def __str__(self):
        return "[TM=" + repr(self.name()) + ", DESC=" + repr(self.description()) + ", RAW=" + repr(self._getEng()) + "]" 

################################################################################
