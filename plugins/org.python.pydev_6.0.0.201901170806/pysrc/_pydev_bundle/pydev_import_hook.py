
import sys
from types import ModuleType


class ImportHookManager(ModuleType):
    def __init__(self, name, system_import):
        ModuleType.__init__(self, name)
        self._system_import = system_import
        self._modules_to_patch = {}
        self.import_in_progress = False
        self._loaded = {}
        self.loaded_modules = {}
        self.skipCache = False
    def add_module_name(self, module_name, activate_function):
        self._modules_to_patch[module_name] = activate_function

    def do_import(self, name, *args, **kwargs):
        activate_func = None
        if name in self._modules_to_patch:
            activate_func = self._modules_to_patch.pop(name)
             
        #print 'import ' + str(name)
        try:
            module = self._system_import(name, *args, **kwargs)
        except:

            raise 
        #print 'load ' + name
        #module = self._system_import(name, *args, **kwargs)

        try:
            if activate_func:
                activate_func() #call activate function
        except:
            sys.stderr.write("Matplotlib support failed\n")
            
        if str(name) in ['__main__','ONBOARD']:
            if module:
                sys.modules[module.__name__] = module
            return module
        try:
            
            if name not in self._loaded.keys() and 'built-in' not in str(module) and 'spellwrapper' not in str(name):

                self._loaded[name] = True
                #print 'add spell to ' + name
                if len(args) > 0:
                    for key in args[0].keys():
                        if key not in module.__dict__:
                            module.__dict__[key] = args[0][key]
                if '__main__' not in str(name):
                    try:
                        import spelldebugger.spellwrapper as spell   # @UnresolvedImport
                        for key in spell.__dict__.keys():
                            if key not in module.__dict__:
                                module.__dict__[key] = spell.__dict__[key]
                    except:
                        pass
                    #print 'finished adding spell to ' + str(name)
                
            else:
                pass
        except:
            pass
            #print 'failed adding spell to ' + str(name) + ' reason:' + str(sys.exc_info())
        if module:
            sys.modules[module.__name__] = module
        return module

if sys.version_info[0] >= 3:
    import builtins # py3
else:
    import __builtin__ as builtins

import_hook_manager = ImportHookManager(__name__ + '.import_hook', builtins.__import__)
builtins.__import__ = import_hook_manager.do_import
sys.modules[import_hook_manager.__name__] = import_hook_manager
del builtins