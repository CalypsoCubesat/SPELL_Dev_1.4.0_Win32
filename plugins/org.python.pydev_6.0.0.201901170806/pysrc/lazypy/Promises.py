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

import functools
import sys
from lazypy.Utils import *

__all__ = ["force",
           "PromiseMetaClass",
           "Promise",
           "LoggingMetaClass",
           "LoggingValue",
          ]

def force(value):
    """
    This helper function forces evaluation of a promise. A promise
    for this function is something that has a __force__ method (much
    like an iterator in python is anything that has a __iter__
    method).
    """

    f = getattr(value, '__force__', None)
    return f() if f else value

class PromiseMetaClass(type):

    """
    This meta class builds the behaviour of promise classes. It's mainly
    building standard methods with special behaviour to mimick several
    types in Python.
    
    The __magicmethods__ list defines what magic methods are created. Only
    those magic methods are defined that are not already defined by the
    class itself.
    
    __magicrmethods__ is much like __magicmethods__ only that it provides
    both the rmethod and the method so the proxy can decide what to use.
    
    The __magicfunctions__ list defines methods that should be mimicked by
    using some predefined function.
    
    The promise must define a __force__ method that will force evaluation
    of the promise.
    """

    __magicmethods__ = ['__abs__', 
                        '__pos__', 
                        '__invert__', 
                        '__neg__',
                        '__reversed__',
                       ]
    
    __magicrmethods__ = [('__radd__', '__add__'), 
                         ('__rsub__', '__sub__'),
                         ('__rdiv__', '__div__'), 
                         ('__rmul__', '__mul__'),
                         ('__rand__', '__and__'), 
                         ('__ror__', '__or__'),
                         ('__rxor__', '__xor__'), 
                         ('__rlshift__', '__lshift__'),
                         ('__rrshift__', '__rshift__'), 
                         ('__rmod__', '__mod__'),
                         ('__rdivmod__', '__divmod__'), 
                         ('__rtruediv__', '__truediv__'),
                         ('__rfloordiv__', '__floordiv__'), 
                         ('__rpow__', '__pow__'),
                         ('__req__', '__eq__'),
                         ('__rlt__', '__lt__'),
                         ('__rle__', '__le__'),
                         ('__rne__', '__ne__'),
                         ('__rgt__', '__gt__'),
                         ('__rge__', '__ge__'),
                        ]
    
    __magicfunctions__ = [('__cmp__', cmp), 
                          ('__str__', str),
                          ('__unicode__', unicode), 
                          ('__complex__', complex),
                          ('__int__', int), 
                          ('__long__', long), 
                          ('__float__', float),
                          ('__oct__', oct), 
                          ('__hex__', hex), 
                          ('__hash__', hash),
                          ('__len__', len), 
                          ('__iter__', iter), 
                          ('__delattr__', delattr),
                          ('__setitem__', setitem), 
                          ('__delitem__', delitem),
                          ('__setslice__', setslice), 
                          ('__delslice__', delslice),
                          ('__getitem__', getitem), 
                          ('__call__', apply),
                          ('__getslice__', getslice), 
                          ('__nonzero__', bool),
                          ('__bool__', bool),
                         ]

    def __init__(klass, name, bases, attributes):
        for k in klass.__magicmethods__:
            if k not in attributes:
                setattr(klass, k, klass.__forcedmethodname__(k))
        for (k, v) in klass.__magicrmethods__:
            if k not in attributes:
                setattr(klass, k, klass.__forcedrmethodname__(k, v))
            if v not in attributes:
                setattr(klass, v, klass.__forcedrmethodname__(v, k))
        for (k, v) in klass.__magicfunctions__:
            if k not in attributes:
                setattr(klass, k, klass.__forcedmethodfunc__(v))
        super(PromiseMetaClass, klass).__init__(name, bases, attributes)

    def __forcedmethodname__(self, method):
        """
        This method builds a forced method. A forced method will
        force all parameters and then call the original method
        on the first argument. The method to use is passed by name.
        """

        def wrapped_method(self, *args, **kwargs):
            result = force(self)
            meth = getattr(result, method)
            args = [force(arg) for arg in args]
            kwargs = dict([(k,force(v)) for k,v in kwargs.items()])
            return meth(*args, **kwargs)

        return wrapped_method
    
    def __forcedrmethodname__(self, method, alternative):
        """
        This method builds a forced method. A forced method will
        force all parameters and then call the original method
        on the first argument. The method to use is passed by name.
        An alternative method is passed by name that can be used
        when the original method isn't availabe - but with reversed
        arguments. This can only handle binary methods.
        """

        def wrapped_method(self, other):
            self = force(self)
            other = force(other)
            meth = getattr(self, method, None)
            if meth is not None:
                res = meth(other)
                if res is not NotImplemented:
                    return res
            meth = getattr(other, alternative, None)
            if meth is not None:
                res = meth(self)
                if res is not NotImplemented:
                    return res
            return NotImplemented

        return wrapped_method
    
    def __forcedmethodfunc__(self, func):
        """
        This method builds a forced method that uses some other
        function to accomplish it's goals. It forces all parameters
        and then calls the function on those arguments.
        """

        def wrapped_method(*args, **kwargs):
            args = [force(arg) for arg in args]
            kwargs = dict([(k,force(v)) for k,v in kwargs.items()])
            return func(*args, **kwargs)

        return wrapped_method
    
    def __delayedmethod__(self, func):
        """
        This method builds a delayed method - one that accomplishes
        it's choire by calling some function if itself is forced.
        A class can define a __delayclass__ if it want's to
        override what class is created on delayed functions. The
        default is to create the same class again we are already
        using.
        """

        def wrapped_method(*args, **kw):
            klass = args[0].__class__
            klass = getattr(klass, '__delayclass__', klass)
            return klass(func, args, kw)

        return wrapped_method
    
# It's awful, but works in Python 2 and Python 3
Promise = PromiseMetaClass('Promise', (object,), {})
class Promise(Promise):

    """
    The initialization get's the function and it's parameters to
    delay. If this is a promise that is created because of a delayed
    method on a promise, args[0] will be another promise of the same
    class as the current promise and func will be one of (getattr,
    apply, getitem, getslice). This knowledge can be used to optimize
    chains of delayed functions. Method access on promises will be
    factored as one getattr promise followed by one apply promise.
    """

    def __init__(self, func, args, kw):
        """
        Store the object and name of the attribute for later
        resolving.
        """
        self.__func = func
        self.__args = args
        self.__kw = kw
        self.__result = NoneSoFar
    
    
    
    def __force__(self):
        """
        This method forces the value to be computed and cached
        for future use. All parameters to the call are forced,
        too.
        """

        if self.__result is NoneSoFar:
            args = [force(arg) for arg in self.__args]
            kw = dict([(k, force(v)) for (k, v) in self.__kw.items()])
            self.__result = self.__func(*args, **kw)
        return self.__result
    
    def __repr__(self):
        if self.__result != NoneSoFar:
            return repr(self.__result)
        else:
            return '<delayed evaluation>'

class LoggingMetaClass(type):
    """
    This meta class builds the behaviour of promise classes. It's mainly
    building standard methods with special behaviour to mimick several
    types in Python.
    
    The __magicmethods__ list defines what magic methods are created. Only
    those magic methods are defined that are not already defined by the
    class itself.
    
    __magicrmethods__ is much like __magicmethods__ only that it provides
    both the rmethod and the method so the proxy can decide what to use.
    
    The __magicfunctions__ list defines methods that should be mimicked by
    using some predefined function.
    
    The promise must define a __force__ method that will force evaluation
    of the promise.
    """
    __magicmethods__ = ['__abs__', 
                        '__pos__', 
                        '__invert__', 
                        '__neg__',
                        '__reversed__',
                       ]
    
    __magicrmethods__ = [('__radd__', '__add__'), 
                         ('__rsub__', '__sub__'),
                         ('__rdiv__', '__div__'), 
                         ('__rmul__', '__mul__'),
                         ('__rand__', '__and__'), 
                         ('__ror__', '__or__'),
                         ('__rxor__', '__xor__'), 
                         ('__rlshift__', '__lshift__'),
                         ('__rrshift__', '__rshift__'), 
                         ('__rmod__', '__mod__'),
                         ('__rdivmod__', '__divmod__'), 
                         ('__rtruediv__', '__truediv__'),
                         ('__rfloordiv__', '__floordiv__'), 
                         ('__rpow__', '__pow__'),
                         ('__req__', '__eq__'),
                         ('__rlt__', '__lt__'),
                         ('__rle__', '__le__'),
                         ('__rne__', '__ne__'),
                         ('__rgt__', '__gt__'),
                         ('__rge__', '__ge__'),
                        ]
    
    __magicfunctions__ = [('__cmp__', cmp), 
                          ('__str__', str),
                          ('__unicode__', unicode), 
                          ('__complex__', complex),
                          ('__int__', int), 
                          ('__long__', long), 
                          ('__float__', float),
                          ('__oct__', oct), 
                          ('__hex__', hex), 
                          ('__hash__', hash),
                          ('__len__', len), 
                          ('__iter__', iter), 
                          ('__delattr__', delattr),
                          ('__setitem__', setitem), 
                          ('__delitem__', delitem),
                          ('__setslice__', setslice), 
                          ('__delslice__', delslice),
                          ('__getitem__', getitem), 
                          ('__call__', apply),
                          ('__getslice__', getslice), 
                          ('__nonzero__', bool),
                          ('__bool__', bool),
                         ]

    def __init__(self, name, bases, attributes):
        for k in self.__magicmethods__:
            if k not in attributes:
                setattr(self, k, self.__forcedmethodname__(k))
        for (k, v) in self.__magicrmethods__:
            if k not in attributes:
                setattr(self, k, self.__forcedrmethodname__(k, v))
            if v not in attributes:
                setattr(self, v, self.__forcedrmethodname__(v, k))
        for (k, v) in self.__magicfunctions__:
            if k not in attributes:
                setattr(self, k, self.__forcedmethodfunc__(v))
        super(LoggingMetaClass, self).__init__(name, bases, attributes)

    def __forcedmethodname__(self, method):
        """
        This method builds a forced method. A forced method will
        force all parameters and then call the original method
        on the first argument. The method to use is passed by name.
        """

        def wrapped_method(self, *args, **kwargs):
            result = force(self)
            meth = getattr(result, method)
            args = [force(arg) for arg in args]
            kwargs = dict([(k,force(v)) for k,v in kwargs.items()])
            newResult = meth(*args, **kwargs)
            #print 'called 1 ' + method + ' on ' + repr(result) + ', ' + repr(args) + ', ' + repr(kwargs) + ' ==> ' + repr(newResult)
            argExpr = ''
            for a in args:
                if argExpr:
                    argExpr += ', ' + repr(a)
                else:
                    argExpr = repr(a)
            newExpr = method + '(' + self.getLog() + argExpr + ')'
            print '1:' + newExpr
            return self.__class__(newResult,newExpr,self)

        return wrapped_method
    
    def __forcedrmethodname__(self, method, alternative):
        """
        This method builds a forced method. A forced method will
        force all parameters and then call the original method
        on the first argument. The method to use is passed by name.
        An alternative method is passed by name that can be used
        when the original method isn't availabe - but with reversed
        arguments. This can only handle binary methods.
        """

        def wrapped_method(oself, other):
            self = force(oself)
            other = force(other)
            meth = getattr(self, method, None)
            if meth is not None:
                res = meth(other)
                if res is not NotImplemented:
                    #print 'called 2 ' + method + ' on ' + repr(self) + ', ' + repr(other) + ' ==> ' + repr(res)
                    newExpr = method + '(' + oself.getLog() + ', ' + repr(other) + ')'
                    print '2:' + newExpr
                    if method == '__eq__' or method == '__ne__' or method == '__req__' or method == '__rne__':
                        oself.addExpr([newExpr])
                        bool(oself.__class__(res,newExpr,oself))
                    return oself.__class__(res,newExpr,oself)
            meth = getattr(other, alternative, None)
            if meth is not None:
                res = meth(self)
                if res is not NotImplemented:
                    #print 'called 3 ' + alternative + ' on ' + repr(self) + ', ' + repr(other) + ' ==> ' + repr(res)
                    newExpr = alternative + '(' + oself.getLog() + ', ' + repr(other) + ')'
                    print '3:' + newExpr
                    if method == '__eq__' or method == '__ne__' or method == '__req__' or method == '__rne__':
                        oself.addExpr([newExpr])
                        bool(oself.__class__(res,newExpr,oself))
                    return oself.__class__(res,newExpr,oself)
            return NotImplemented

        return wrapped_method
    
    def __forcedmethodfunc__(self, func):
        """
        This method builds a forced method that uses some other
        function to accomplish it's goals. It forces all parameters
        and then calls the function on those arguments.
        """

        def wrapped_method(*args, **kwargs):
            nargs = [force(arg) for arg in args]
            nkwargs = dict([(k,force(v)) for k,v in kwargs.items()])
            res = func(*nargs, **nkwargs)
            #print 'called 4 ' + func.__name__ + ' on ' + repr(nargs) + ', ' + repr(nkwargs) + ' ==> ' + repr(res)
            logObj1 = getattr(args[0], '_log','')
            if len(args) > 1:
                logObj2 = getattr(args[1], '_log','')
            else:
                logObj2 = ''
            if logObj1 or logObj2:
                if logObj1:
                    expr = logObj1
                else:
                    expr = repr(args[0])
                if logObj2:
                    if expr:
                        expr += ', ' + logObj2
                    else:
                        expr = logObj2
                elif len(args) > 1:
                    if expr:
                        expr += ', ' + repr(args[1])
                    else:
                        expr = args[1]
                if func.__name__ in ['len','int','float','long','bool','str','getslice']:
                    fullFunction = func.__name__ + '(' + expr  + ')'
                else:
                    fullFunction = func.__name__ + '(' + expr  + ')' # == ' +  repr(res)
                print '4:' + fullFunction


            #ENDIF
            if logObj1:
                source = args[0]
            else:
                source = args[1]
            print func.__name__
            if func.__name__ not in ['int','float','long','bool','len','str','getslice']:
                if logObj1:
                    #setattr(args[0], '_log', fullFunction)
                    args[0].addExpr([fullFunction])
                if logObj2:
                    #setattr(args[1], '_log', fullFunction)
                    args[1].addExpr([fullFunction])
                return source.__class__(res,fullFunction,source)
            
            return res

        return wrapped_method
    
    def __delayedmethod__(self, func):
        """
        This method builds a delayed method - one that accomplishes
        it's choire by calling some function if itself is forced.
        A class can define a __delayclass__ if it want's to
        override what class is created on delayed functions. The
        default is to create the same class again we are already
        using.
        """

        def wrapped_method(*args, **kw):
            klass = args[0].__class__
            klass = getattr(klass, '__delayclass__', klass)
            return klass(func, args, kw)

        return wrapped_method



LoggingValue = LoggingMetaClass('LoggingValue', (object,), {})
class LoggingValue(LoggingValue):
    
    exprList = []
    
    """
    The initialization get's the function and it's parameters to
    delay. If this is a promise that is created because of a delayed
    method on a promise, args[0] will be another promise of the same
    class as the current promise and func will be one of (getattr,
    apply, getitem, getslice). This knowledge can be used to optimize
    chains of delayed functions. Method access on promises will be
    factored as one getattr promise followed by one apply promise.
    """
    
    def __init__(self, value, prev=None,parent=None):
        """
        Store the object and name of the attribute for later
        resolving.
        """
        if prev != None:
            self._log = prev # + '==>' + repr(value)
        else:
            self._log = str(value)
        self.__value = value
        if isinstance(parent,LoggingValue):
            self._expr = parent._expr
        else:
            self._expr = LoggingValue.exprList
        
    def getLog(self):
        return self._log
    
    def addExpr(self,exprList):
        for l in exprList:
            if not l in self._expr:
                self._expr += [l]
            else:
                del self._expr[self._expr.index(l)]
                self._expr += [l]
    def __value__(self):
        return self.__value
    
    def __force__(self):
        """
        This method forces the value to be computed and cached
        for future use. All parameters to the call are forced,
        too.
        """

        return self.__value
    
    def __repr__(self):
        return repr(self.__value)
    

# import __builtin__
# 
# BuiltInWrapper = PromiseMetaClass('BuiltInWrapper', (object,), {})
# class BuiltInWrapper(BuiltInWrapper):
#     def __init__(self,oldType):
#         self._oldType = oldType
#          
#     def __instancecheck__(self,*args):
#         return isinstance(args[0], self._oldType)
#      
#     def __call__(self,*args,**kargs):
#         if hasattr(args[0], '__value__'):
#             return args[0].__class__(self._oldType(args[0],**kargs),self._oldType.__name__ + '(' + args[0]._log + ')' ,args[0])
#  
#         return self._oldType(*args,**kargs)
#     
#     def __eq__(self,*args,**kargs):
#         return self._oldType == args[0]
#     def __ne__(self,*args,**kargs):
#         return self._oldType != args[0]
#     
# __builtin__.str = BuiltInWrapper(str)
# __builtin__.len = BuiltInWrapper(len)
# __builtin__.int = BuiltInWrapper(int)
# __builtin__.long = BuiltInWrapper(long)
# __builtin__.float = BuiltInWrapper(float)
# __builtin__.bool = BuiltInWrapper(bool)
# 
# 
# del __builtin__