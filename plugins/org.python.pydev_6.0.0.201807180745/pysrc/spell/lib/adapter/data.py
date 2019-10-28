###################################################################################
## MODULE     : spell.lib.adapter.data
## DATE       : Mar 18, 2011
## PROJECT    : SPELL
## DESCRIPTION: Hook for the C++ data containers
## -------------------------------------------------------------------------------- 
##
##  Copyright (C) 2008, 2015 SES ENGINEERING, Luxembourg S.A.R.L.
##
##  This file is part of SPELL.
##
## This component is free software: you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License and GNU General Public License (to which the GNU Lesser
## General Public License refers) along with this library.
## If not, see <http://www.gnu.org/licenses/>.
##
###################################################################################

#*******************************************************************************
# SPELL Imports
#*******************************************************************************
import sys
_dta_failed = True

try:
    import libSPELL_DTA
    _dta_failed=False
except ImportError,ex:
    sys.stderr.write("FATAL: unable to import DTA interface\n")

#*******************************************************************************
# Local Imports
#*******************************************************************************

#*******************************************************************************
# System Imports
#*******************************************************************************


###############################################################################
# Module import definition

__all__ = ['DataContainer,Var']

if not _dta_failed:
    global DataContainer,Var
    DataContainer = libSPELL_DTA.DataContainer
    Var = libSPELL_DTA.Var
else:
    DataContainer = {}
    Var = {}
