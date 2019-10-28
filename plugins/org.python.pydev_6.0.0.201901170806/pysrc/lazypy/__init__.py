"""
Lazy Evaluation for Python - main package with primary exports

Copyright (c) 2004, Georg Bauer <gb@murphy.bofh.ms>, 
Copyright (c) 2011, Alexander Marshalov <alone.amper@gmail.com>, 
except where the file explicitly names other copyright holders and licenses.

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 
the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys

#assert sys.hexversion >= 0x02070000, 'at least Python 2.7 is needed'

__version__ = "0.6"
__all__ = ["Promise",
           "PromiseMetaClass",
           "force",
           "LazyEvaluated",
           "LazyEvaluatedMetaClass",
           "delay",
           "lazy"
          ]

from lazypy.Promises import Promise, PromiseMetaClass, force
from lazypy.LazyClasses import LazyEvaluated, LazyEvaluatedMetaClass
from lazypy.Functions import delay, lazy
from lazypy.Utils import NoneSoFar

import __builtin__
oldType = __builtin__.type
def force(value):
    """
    This helper function forces evaluation of a promise. A promise
    for this function is something that has a __force__ method (much
    like an iterator in python is anything that has a __iter__
    method).
    """

    f = getattr(value, '__force__', None)
    return f() if f else value
# class my_type(object):
#     def __init__(self,oldType,*args,**kargs):
#         self._oldType = oldType
#         if hasattr(oldType, '__dict__'):
#             self.__dict__.update(oldType.__dict__)
#         
#     def __instancecheck__(self,*args):
#         return isinstance(args[0], self._oldType)
#     
#     def __call__(self,*args,**kargs):
#         if hasattr(args[0], '__value__'):
#             return self(args[0].__value__(),*args[1:],**kargs)
#         
#         if hasattr(args[0], '__force__'):
#             r = args[0]._Promise__result
#             if r:
#                 return bool
#             return self(force(args[0]),*args[1:],**kargs)
#         #ENDIF
#         return self._oldType(*args,**kargs)
# 
# 
# __builtin__.type = my_type(type)
