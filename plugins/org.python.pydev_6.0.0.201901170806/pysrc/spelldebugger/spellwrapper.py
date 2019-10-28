
# spell imports
from spell.lang.functions import *
from spell.lang.constants import *
from spell.lang.modifiers import *
from spell.lang.user import *
from spell.lib.adapter.utctime import *
from spell.lib.adapter.file import *
from math import *
#from lazypy import delay
import threading


# system imports
import os, sys, glob, random, inspect,time
from spell.lib.adapter.result import PtcResult
from time import sleep
from _pydevd_bundle.pydevd_constants import STATE_RUN, PYTHON_SUSPEND
import string
# random seed
seed = os.getenv("SPELL_RANDOM_SEED")

PROC = {}
ARGS = {}
IVARS = {}
import __main__

__main__.PROC = PROC
if seed:
    random.seed(seed)
def HandleException():
    print 'Exception caught','\n'
    print sys.exc_info()
    raise sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]

# context
from pydevd import SetupHolder,process_command_line
use_remote_driver = False
setup = None
if not SetupHolder.setup:
    try:
        if 'original_argv' not in  sys.__dict__.keys():
            sys.original_argv = sys.argv[:]
        setup = process_command_line(sys.original_argv[:])
        SetupHolder.setup = setup
    except ValueError:
        print 'ERROR while parsing args'
    #ENDTRY
#ENDIF
if SetupHolder.setup:
    use_remote_driver = SetupHolder.setup['use-remote-driver']
    if use_remote_driver:
        use_remote_port = SetupHolder.setup['use-remote-port']
#ENDIF
FUNCTION_REGISTRY = {}
TM_ITEM_PROXY = {}
def __init_SPELL():
    return True


def skipToCurrentLine():
        thread = threading.currentThread()  
        if REGISTRY['SILENT']:
            return
        reset_Thread_State = False
        try:
            if thread.additional_info.pydev_step_cmd != -1:
                thread.additional_info.suspend_type = PYTHON_SUSPEND
                thread.additional_info.pydev_state = 1
                thread.stop_reason = "1090"
            else:
                thread.stop_reason = "1090"
                thread.additional_info.pydev_state = 2
                thread.additional_info.pydev_step_cmd = 1060
                reset_Thread_State = True
            #ENDIF
        except:
            pass
        try:
            if reset_Thread_State and thread.stop_reason == "1090":
                #print '-' * 15
                #print thread.additional_info.pydev_state
                #print thread.additional_info.pydev_step_cmd
                #print thread.stop_reason
                #print '-' * 15
                #
                thread.additional_info.suspend_type = PYTHON_SUSPEND
                thread.additional_info.pydev_state = 1
                thread.additional_info.pydev_step_cmd = -1
            #ENDIF
        except:
            pass
        
if use_remote_driver:
    try:
        context = 'RemoteSPELLHiFly'
        os.environ['SPELL_CONTEXT'] = context
        print 'Starting Remote SPELL driver.'
        print 'Please start the remote SPELL server on port ' + str(use_remote_port) + '.'
    
        from spell.config.reader import Config
        SPELL_CONFIG = os.getenv("SPELL_CONFIG")
        if not SPELL_CONFIG:
            import spelldebugger as debugger
            SPELL_CONFIG = os.path.dirname(debugger.__file__) + os.sep + "config"
            
            del debugger
            os.environ['SPELL_CONFIG'] = SPELL_CONFIG
            os.environ['SPELL_HOME'] = os.path.dirname(SPELL_CONFIG)
        SPELL_DATA =  os.getenv("SPELL_DATA")
        if not SPELL_DATA:
            for p in sys.path:
                if 'UserLib' in p:
                    userlib = p + os.sep + "*.py"
                    SPELL_DATA = os.path.dirname(p)
                    os.environ['SPELL_DATA'] = SPELL_DATA
                    break
        else:
            userlib = SPELL_DATA + os.sep + "UserLib" + os.sep + "*.py"
        # import all userlib files
        
        config = SPELL_CONFIG + os.sep + "contexts" + os.sep + "server_" + context + ".xml"
        Config.instance().load(config)
        
        # driver
        from spell.lib.drivermgr import DriverManager
        DriverManager.instance().setup(context)
        from spell.lib.adapter.dbmgr import DBMGR
        REGISTRY['CTX']['satname'] = os.path.split(os.environ['SPELL_DATA'])[-1]
        os.environ['SPELL_DATA'] = os.path.dirname(os.environ['SPELL_DATA'])
        SCDB = DBMGR.loadDatabase("SCDB")
        GDB = DBMGR.loadDatabase("GDB")
    except:
        import traceback
        traceback.print_exc()
        from spell.lib.drivermgr import DriverManager
        from spell.lib.adapter.dbmgr import DBMGR
        DBMGR.cleanup()
        DriverManager.instance().cleanup()
        print 'Failed to Load HiFly environment.'
        print 'Switching to Scorpio'
        context = 'RemoteSPELLScorpio'
        os.environ['SPELL_CONTEXT'] = context
        print 'Starting Remote SPELL driver.'
        print 'Please start the remote SPELL server on port ' + str(use_remote_port) + '.'
    
        from spell.config.reader import Config
        SPELL_CONFIG = os.getenv("SPELL_CONFIG")
        if not SPELL_CONFIG:
            import spelldebugger as debugger
            SPELL_CONFIG = os.path.dirname(debugger.__file__) + os.sep + "config"
            
            del debugger
            os.environ['SPELL_CONFIG'] = SPELL_CONFIG
            os.environ['SPELL_HOME'] = os.path.dirname(SPELL_CONFIG)
        SPELL_DATA =  os.getenv("SPELL_DATA")
        for p in sys.path:
            if 'UserLib' in p:
                userlib = p + os.sep + "*.py"
                SPELL_DATA = os.path.dirname(p)
                os.environ['SPELL_DATA'] = SPELL_DATA
                break

        # import all userlib files

        config = SPELL_CONFIG + os.sep + "contexts" + os.sep + "server_" + context + ".xml"
        Config.instance().load(config)
        
        # driver
        from spell.lib.drivermgr import DriverManager
        DriverManager.instance().setup(context)
        from spell.lib.adapter.dbmgr import DBMGR
        REGISTRY['CTX']['satname'] = os.path.split(os.environ['SPELL_DATA'])[-1]
        print REGISTRY['CTX']['satname']
        os.environ['SPELL_DATA'] = os.path.dirname(os.environ['SPELL_DATA'])
        SCDB = DBMGR.loadDatabase("SCDB")
        GDB = DBMGR.loadDatabase("GDB")
    #ENDTRY
    
    # databases
    from _pydevd_bundle.pydevd_comm import GetGlobalDebugger
            
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
        value = str(REGISTRY['CIF'].prompt(currentHint,opt,config))
        try :
            return eval(value)
        except:
            return value
        
    import xmlrpclib
    import httplib
    class SPELLDebugServerProxy(object):
        
        def __init__(self, url):
            self._xmlrpc_server_proxy = xmlrpclib.ServerProxy(url,allow_none=True)
        def __getattr__(self, name):
            call_proxy = getattr(self._xmlrpc_server_proxy, name)
            def _call(*args, **kwargs):
                if 'HandleError' in kwargs:
                    shouldHandleError = kwargs['HandleError']
                else:
                    shouldHandleError = True
                if name != 'listMethods':
                    kwargs['HandleError'] = False
                while True:
                    if name not in ['Display','Finish','listMethods']:
                        skipToCurrentLine()
                        print '\t\t>>Remote ' + str(name) + '(' + repr(args)[1:-1] + repr(kwargs) + ')'
                        try:
                            REGISTRY['REMOTE'].Display('<<Received ' + str(name) + '(' + repr(args)[1:-1] + repr(kwargs) + ')')
                            try:
                                value = call_proxy(args, kwargs)
                            except:
                                import traceback
                                msg = traceback.format_exc()
                                #print msg
                                if 'got an unexpected keyword argument \'HandleError\'">' in msg and 'HandleError' in kwargs:
                                    del kwargs['HandleError']
                                    sys.exc_clear()
                                    value = call_proxy(args, kwargs)
                                else:
                                    raise sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]
                            REGISTRY['REMOTE'].Display('>>Finished ' + str(name))
                            print '\t\t<<Remote ' + str(name) + ' = ' + repr(value)
                            return value
                        except xmlrpclib.ProtocolError,ex:
                            sys.stderr.write('\t\t Could not connect to remote server. Retrying\n')
                            time.sleep(2)
                            sys.exc_clear()
                            continue
                        except httplib.BadStatusLine,ex:
                            sys.stderr.write('\t\t Could not connect to remote server. Retrying\n')
                            time.sleep(2)
                            sys.exc_clear()
                            continue
                        except:
                            if shouldHandleError:
                                import traceback
                                from spell.lib.exception import DriverException
                                traceback.print_exc()
                                error = string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
                                
                                sys.exc_clear()

                                f_name = str(name) + '(' + repr(args)[1:-1] + repr(kwargs) + ')'
                                error_msg = 'Error while executing function ' + str(f_name) + '!\n'+\
                                            'Caught Exception:\n' + str(error).replace('\\n', '\n\t\t\t')
                                options = ['Retry:Retry this function',
                                           'Skip:Skip this function and return True',
                                           'Enter On Demand:Skip this function and enter a value on demand',
                                           'Cancel:Skip this function and return False']
                                action = Prompt(error_msg,options,LIST)
                                print action
                                if action == 'Retry':
                                    continue
                                elif action == 'Skip':
                                    print 'Skipping function ' + str(name) + ', returning True.'
                                    return True
                                elif action == 'Cancel':
                                    print 'Canceling function ' + str(name) + ', returning False.'
                                    return False
                                elif action == 'Enter On Demand':
                                    print 'Skipping function ' + str(name) + ', procedure will ask for a value if required.'
                                    query = delay(PromptWithCurrentText,('Please enter a SPELL statement for the function call ' + str(f_name) + '\n',None,{'Type':ALPHA}))
                                    return query
                                del traceback
                            else:
                                raise sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
                        #ENDTRY
                    else:
                        return call_proxy(args, kwargs)
                #ENDWHILE
            _call.__name__ = name
            return _call
    def __init_SPELL():
        global REGISTRY
        print 'Trying to connect to remote host http://localhost:' + str(SetupHolder.setup['use-remote-port'])
        REGISTRY['REMOTE'] = SPELLDebugServerProxy('http://localhost:' + str(SetupHolder.setup['use-remote-port']))
       
        import time
        limit = 20
        while True:
            try:
                limit -= 1
                methods = REGISTRY['REMOTE'].listMethods()
                sys.stderr.write('Remote connection established.\n')
                break
            except:
                sys.stderr.write('Could not connect to debug server. Retrying.\n')
                if limit <= 0:
                    import traceback
                    sys.stderr.write("Could not connect to remote server!\n")
                    traceback.print_exc()
                    sys.exit()
                time.sleep(1)
        SPELL_REMOTE_EXCEPTION_FILTER = ['Display','Event','Abort','Finish','Step','Prompt','Goto','LoadDictionary','CreateDictionary','SaveDictionary','DeleteDictionary','listMethods','ReadDirectory','OpenFile','CloseFile','ReadFile']
        import spell.lang.functions as spell_lib
        for method in methods:
            if method not in SPELL_REMOTE_EXCEPTION_FILTER:
                globals()[method] =  REGISTRY['REMOTE'].__getattr__(method)
                while True:
                    try:
                        for mod_name,mod in sys.modules.iteritems():
                            if mod:
                                mod.__dict__[method] = REGISTRY['REMOTE'].__getattr__(method)
                        globals()[method] = REGISTRY['REMOTE'].__getattr__(method)
                        break
                    except RuntimeError,ex:
                        continue
                    except:
                        import traceback
                        traceback.print_exc()
                        print 'Skipping ' + method
                        break
        #ENDFOR
        from spell.lib.adapter.utctime import TIME
        from xmlrpclib import Marshaller
        from xmlrpclib import Unmarshaller
        from spell.lib.adapter.result import TmResult,PtcResult
        from RemoteSPELL.interface.tc_sim_item import TcItemSimClass,PtcItemSimClass
        from RemoteSPELL.interface.tm_sim_item import TmItemSimClass
        from spell.lib.registry import REGISTRY
        
        def dump_TmResult(self,value,write):
            write("<value><boolean>")
            write(value and "1" or "0")
            write("</boolean></value>\n")
        
        def dump_TIME(self,value,write):
            write("<value><SPELLTime>")
            write(str(value))
            write("</SPELLTime></value>\n")
        def create_TIME(self,value):
            self.append(TIME(value.strip())) 
            
        def dump_TcItemClass(self,value,write):
            write("<value><TcItemClass>")
            write(value.name())
            write("</TcItemClass></value>\n")
        def create_TcItemClass(self,value):
            self.append(REGISTRY['SIM'].getTCProxy(value))
            
        def dump_PtcItemClass(self,value,write):
            write("<value><PtcItemClass>")
            write(value.name())
            write("</PtcItemClass></value>\n")
        def create_PtcItemClass(self,value):
            self.append(REGISTRY['SIM'].getPTCProxy(value))
            
        def dump_TmItemClass(self,value,write):
            write("<value><TmItemClass>")
            write(value.proxyName())
            write("</TmItemClass></value>\n")
        def create_TmItemClass(self,value):
            self.append(REGISTRY['SIM'].getTMProxy(value))
            
        def dump_function(self,value,write):
            global FUNCTION_REGISTRY
            try:
                FUNCTION_REGISTRY[value.__name] = value
                write("<value><function>")
                write(str(value.__name))
                write("</function></value>\n")
            except:
                FUNCTION_REGISTRY[value.__name__] = value
                write("<value><function>")
                write(str(value.__name__))
                write("</function></value>\n")
            pass
        def create_function(self,value):
            global FUNCTION_REGISTRY
            if value in FUNCTION_REGISTRY.keys():
                local_function = FUNCTION_REGISTRY[value]
            elif value in globals().keys():
                local_function = globals()[value]
            else:
                return
            self.append(local_function)
        
        def create_PtcResult(self,value):
            values = value.split('||')
            result = PtcResult()
            result['code']    = eval(values[0])
            result['success'] = eval(values[1])
            result['data']    = eval(values[2])
            result['stage']   = eval(values[3])
            result['error']   = eval(values[4])
            self.append(result)
        
        Marshaller.dispatch[TmResult] = dump_TmResult
        Marshaller.dispatch[TIME] = dump_TIME
        Marshaller.dispatch[TcItemSimClass] = dump_TcItemClass
        Marshaller.dispatch[PtcItemSimClass] = dump_PtcItemClass
        Marshaller.dispatch[type(dump_function)] = dump_function
        
        Unmarshaller.dispatch['SPELLTime'] = create_TIME
        Unmarshaller.dispatch['TcItemClass'] = create_TcItemClass
        Unmarshaller.dispatch['PtcItemClass'] = create_PtcItemClass
        
        Unmarshaller.dispatch['function'] = create_function
        
        Marshaller.dispatch[TmItemSimClass] = dump_TmItemClass
        Unmarshaller.dispatch['TmItemClass'] = create_TmItemClass
        
        Marshaller.dispatch[type(0L)] = lambda _, v, w: w("<value><long>%d</long></value>" % v)
        Unmarshaller.dispatch['long'] = lambda s,v: s.append(long(v))
        
        Marshaller.dispatch[PtcResult] = lambda _, v, w: w(("<value><PtcResult>%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "</PtcResult></value>") % (repr(v.code()),repr(v.success()),repr(v.data()),repr(v.stage()),repr(v.error()) ))
        Unmarshaller.dispatch['PtcResult'] = create_PtcResult
        
        return True
    
    import threading
    t = threading.Thread(target=__init_SPELL)
    
    t.start()
else:
    try:
        context = os.getenv("SPELL_CONTEXT")
        if not context:
            context = 'Scorpio'
            os.environ['SPELL_CONTEXT'] = context
        assert context, "spellwrapper needs a context to load"
        
        # config file
        from spell.config.reader import Config
        SPELL_CONFIG = os.getenv("SPELL_CONFIG")
        if not SPELL_CONFIG:
            import spelldebugger as debugger
            SPELL_CONFIG = os.path.dirname(debugger.__file__) + os.sep + "config"
            
            del debugger
            os.environ['SPELL_CONFIG'] = SPELL_CONFIG
            os.environ['SPELL_HOME'] = os.path.dirname(SPELL_CONFIG)
        SPELL_DATA =  os.getenv("SPELL_DATA")
        if not SPELL_DATA:
            for p in sys.path:
                if 'UserLib' in p:
                    userlib = p + os.sep + "*.py"
                    SPELL_DATA = os.path.dirname(p)
                    os.environ['SPELL_DATA'] = SPELL_DATA
                    break
        else:
            userlib = SPELL_DATA + os.sep + "UserLib" + os.sep + "*.py"
        # import all userlib files
        
        config = SPELL_CONFIG + os.sep + "contexts" + os.sep + "server_" + context + ".xml"
        Config.instance().load(config)
        
        # driver
        from spell.lib.drivermgr import DriverManager
        DriverManager.instance().setup(context)
        
        
        # databases
        
        from spell.lib.adapter.dbmgr import DBMGR
        REGISTRY['CTX']['satname'] = os.path.split(os.environ['SPELL_DATA'])[-1]
        os.environ['SPELL_DATA'] = os.path.dirname(os.environ['SPELL_DATA'])
        SCDB = DBMGR.loadDatabase("SCDB")
        GDB = DBMGR.loadDatabase("GDB")
    except:
        import traceback
        traceback.print_exc()
        from spell.lib.drivermgr import DriverManager
        from spell.lib.adapter.dbmgr import DBMGR
        DBMGR.cleanup()
        DriverManager.instance().cleanup()
        context = 'HiFly'
        os.environ['SPELL_CONTEXT'] = context
        assert context, "spellwrapper needs a context to load"
        
        # config file
        from spell.config.reader import Config
        import spelldebugger as debugger
        SPELL_CONFIG = os.path.dirname(debugger.__file__) + os.sep + "config"
        
        del debugger
        os.environ['SPELL_CONFIG'] = SPELL_CONFIG
        os.environ['SPELL_HOME'] = os.path.dirname(SPELL_CONFIG)
        SPELL_DATA =  os.getenv("SPELL_DATA")
    
        for p in sys.path:
            if 'UserLib' in p:
                userlib = p + os.sep + "*.py"
                SPELL_DATA = os.path.dirname(p)
                os.environ['SPELL_DATA'] = SPELL_DATA
                break
    
        # import all userlib files
        
        config = SPELL_CONFIG + os.sep + "contexts" + os.sep + "server_" + context + ".xml"
        Config.instance().load(config)
        
        # driver
        DriverManager.instance().setup(context)
        
        REGISTRY['CTX']['satname'] = os.path.split(os.environ['SPELL_DATA'])[-1]
        
        os.environ['SPELL_DATA'] = os.path.dirname(os.environ['SPELL_DATA'])
        # databases
        SCDB = DBMGR.loadDatabase("SCDB")
        GDB = DBMGR.loadDatabase("GDB")
    #ENDTRY
#ENDIF
import _pydev_bundle.pydev_import_hook as importer
pattern = os.path.expanduser(userlib)
USERLIB_LIST = []
for fn in glob.glob(pattern):
    try:
        try:
            index = fn.rindex('\\')
            if index < 0:
                index = fn.rindex('/')
            last_index = fn.rindex('.py')
            
            module = importer.import_hook_manager.do_import(fn[index+1:last_index],globals())
            #print 'load module ' + str(module)
            for key in module.__dict__.keys():
                if key not in globals().keys():
                    globals()[key] = module.__dict__[key]
                    try:
                        globals()[key].__module__= module
                    except:
                        pass
            USERLIB_LIST += [module]                    
        except:
            print 'load raw ' + str(fn)
            import traceback
            traceback.print_exc()
            del traceback
            execfile(fn)
    except:
        print "Failed to import " + str(fn) + " " + str(sys.exc_info())
        
for userlib in USERLIB_LIST:
    for key in globals().keys():
        if key not in userlib.__dict__.keys():
            userlib.__dict__[key] = globals()[key]
            
            
procframe = inspect.currentframe().f_back
procfilename = procframe.f_code.co_filename
print procframe.f_code.co_filename
procname = os.path.basename(procfilename)
PROC.update({
  'NAME': procname + '#0',
  'PARENT': '\xff',
  'OUTPUT_DATA': SPELL_DATA + os.sep + "OutputFiles",
  'ARGS': '',
  'INPUT_DATA': SPELL_DATA + os.sep + "InputFiles",
  'STEP': None,
  'PREV_STEP': None
})

# define special dicts
# Var definition: Type, Range, Default, Expected, Confirm
def Var(Type, Range=None, Default=None, Expected=None, Confirm=True):
    pass

# Step function definition
def Step(id, descr):
    cif.notify(id, descr)
    setProcStep(id, descr)

def setProcStep(id, descr,skipSuspend=True):
    global PROC
    if PROC['STEP']:
        PROC['PREV_STEP'] = PROC['STEP']
    else:
        PROC['PREV_STEP'] = ['','']
    PROC['STEP'] = [id, descr]
    #try:
    
    source_file = inspect.stack()[2][1]
    print source_file
    REGISTRY['DEBUG'].setNextStep(source_file,PROC['PREV_STEP'][0],PROC['STEP'][0])
    #except:
    #    pass
    if id == 'INIT' and skipSuspend:
        from pydevd import get_global_debugger
        py_debugger = get_global_debugger()
        thread = threading.currentThread()  
        if REGISTRY['SILENT']:
            return
        try:
            py_debugger.set_suspend(thread, 122)
        except:
            pass
        setProcStep(id,descr,False)
        return
    print 'Step ' + str(id) + ': ' + str(descr) + ''

# Class stubs
class SpellCif:
    def setVerbosity(self, *arg):
        pass
    def resetVerbosity(self, *arg):
        pass
    def notify(self, *arg):
        #print repr(arg)
        pass
    def write(self, *arg):
        if (len(arg) == 2):
            msg = arg[0]
            cfg = arg[1]
            print msg
    def prompt(self,message,options,config):
        prompt = "Prompt: " + message + "\n"
        promptTypeDict = {ALPHA:'Alpha',
                          NUM:'Number',
                          DATE:'Date',
                          YES:'YES',
                          NO:'NO',
                          OK:'OK',
                          LIST:'LIST',
                          COMBO:'LIST',
                          YES_NO:'YES|NO',
                          OK_CANCEL:'OK|CANCEL',
                          DATE:'DATE'}
        optionsDict = {}
        if options and type(options) == list:
            prompt += "    available options are: \n"
            for opt in options:
                prompt += "        " +repr(opt) + "\n"
                splittedOpt = str(opt).split(':')
                if len(splittedOpt) > 1 and len(splittedOpt[1].strip()) > 0:
                    optionsDict[splittedOpt[0].strip()] = splittedOpt[1].strip()
                else:
                    optionsDict[splittedOpt[0].strip()] = splittedOpt[0].strip()
            
            promptType = config['Type']
            promptHint = ""
            for mod,desc in promptTypeDict.iteritems():
                if mod & promptType != 0:
                    if promptHint:
                        promptHint += '|' + desc
                    else:
                        promptHint = desc
            prompt += promptHint + "> "
        else:
            promptHint = ""
            promptType = config['Type']

            for mod,desc in promptTypeDict.iteritems():
                if mod & promptType != 0:
                    if promptHint:
                        promptHint += '|' + desc
                    else:
                        promptHint = desc
            prompt += promptHint + "> "
        from _pydevd_bundle.pydevd_comm import GetGlobalDebugger
        
        PyDB = GetGlobalDebugger()
        thread = threading.currentThread()    
        while True:
            try:
                reset_Thread_State = False
                if not REGISTRY['SILENT']:
                    try:
                        if thread.additional_info.pydev_step_cmd != -1:
                            thread.additional_info.suspend_type = PYTHON_SUSPEND
                            thread.additional_info.pydev_state = 1
                            thread.stop_reason = "1090"
                        else:
                            thread.stop_reason = "1090"
                            thread.additional_info.pydev_state = 2
                            thread.additional_info.pydev_step_cmd = 1060
                            reset_Thread_State = True
                        #ENDIF
                    except:
                        pass
                print prompt
                try:
                    import socket
                    while True:
                        try:
                            treatAsSPELL = False
                            if message is None:
                                message = ''
                            if not promptType:
                                promptType = 0
                                treatAsSPELL = True
                            if not options:
                                options = []
                                
                            val = []
                            def ExecuteTrace():
                                a = 1
                                return 2
                            
                            def waitAndExecuteTrace():
                                ExecuteTrace()
                                sleep(0.1)
                                ExecuteTrace()
                                
                            current = threading.currentThread()
                            def getInput(val,message,promptType,options,parentThread=current):
                                val.append(REGISTRY['DEBUG'].requestInput(message,promptType,options))
#                                 print '% received ',val
#                                 def debug(parentThread=parentThread):
#                                     sleep(5)
#                                     frame = sys._current_frames()[parentThread.ident]
#                                     import traceback
#                                     traceback.print_stack(frame)
#                                 worker = threading.Thread(target = debug)
#                                 worker.start()

                            worker = threading.Thread(target = getInput, args=[val,message,promptType,options])
                            worker.start()

                            thread.additional_info.no_wait = True
                            
                            while len(val) == 0:
#                                 print '>>in'
                                PyDB.process_internal_commands()
#                                 print '>>out'
                                #waitAndExecuteTrace()
                            

                            try:
#                                 print 'thread state',reset_Thread_State,thread.stop_reason
                                if reset_Thread_State and thread.stop_reason == "1090":
#                                     print "reseting thread state"
                                    #print '-' * 15
                                    #print thread.additional_info.pydev_state
                                    #print thread.additional_info.pydev_step_cmd
                                    #print thread.stop_reason
                                    #print '-' * 15
                                    #
                                    thread.additional_info.suspend_type = PYTHON_SUSPEND
                                    thread.additional_info.pydev_state = 1
                                    thread.additional_info.pydev_step_cmd = -1
                                #ENDIF
                            except:
                                pass
                            thread.additional_info.no_wait = False
                            val = val[0]
                            
                            if val:
                                try:
                                    import base64
                                    value = base64.standard_b64decode(str(val))
                                except:
                                    value = str(val)
                            else:
                                value = str(val)
                            if value[0] == "'" and value[-1] == "'" and optionsDict:
                                value = value[1:-1]
                                if ':' in value:
                                    value = value.split(':')[0].strip()
                            
                            print '>>>' + str(value)
                            break
                        except socket.error as err:
                            raise err
                        except:
                            import traceback
                            traceback.print_exc()
                            del traceback
                except:
                    print 'Could not connect to SPELL Dev. Switching to manual input\n'
                    value = raw_input('>>>')
                
                
                sys.stdin.flush()
                


                    
                if (OK & promptType or YES & promptType or YES_NO & promptType or OK_CANCEL & promptType) and value.upper() in ['OK','YES',"'OK'","'YES'"]:
                    return True
                if (OK & promptType or YES & promptType or YES_NO & promptType or OK_CANCEL & promptType) and value.upper() in ['NO','CANCEL',"'NO'","'CANCEL'"]:
                    return False
                    
                if NUM & promptType:
                    try :
                        return long(value)
                    except:
                        try:
                            return long(value,16)
                        except:
                            try:
                                return float(value)
                            except:
                                pass
                if ALPHA & promptType and value[0] == "'" and value[-1] == "'":
                    return value[1:-1]
                return value
                
                current_locals = locals()
                
                try: 
                    value = eval(value.strip(),globals(),current_locals)
                except:
                    value = eval("'" + value.strip() + "'",globals(),current_locals)
                #ENDTRY

                return value
            except:
                sys.stderr.write('Could not parse value. '+str(sys.exc_info())+'\n Please try again.\n')
                pass
            finally:
                sys.stdin.flush()
        
cif = SpellCif()
class ProcedureFinished(Exception):
    pass
class ProcedureAborted(Exception):
    pass

class SpellExec:
    def processLock(self, *arg):
        pass
    def processUnlock(self, *arg):
        pass
    def setStep(self, id, descr):
        setProcStep(id, descr)
    def abort(self, *args):
        cif.notify(args)
        if args and len(args) > 0:
            raise ProcedureAborted(args[0])
        raise ProcedureAborted
    def finish(self,*args):
        cif.notify(args)
        if args and len(args) > 0:
            raise ProcedureFinished(args[0])
        raise ProcedureFinished()
    def disableUserAction(self,*args,**kargs):
        pass
    def enableUserAction(self,*args,**kargs):
        pass
    def setUserAction(self,*args,**kargs):
        pass
    
REGISTRY['SILENT'] = False
exc = SpellExec()

REGISTRY['EXEC'] = exc
REGISTRY['CIF'] = cif

### HACK: goto ###
# parse proc for Step calls

def Goto(gotoTarget):
    print "Goto "+str(gotoTarget)
    return
try:
    from pydevd import SetupHolder
    import _pydev_bundle.pydev_localhost as debug_connection
    host = debug_connection.get_localhost()
    if SetupHolder.setup:
        port = SetupHolder.setup['port'] + 3
    else:
        port = debug_connection.get_socket_name()[1]-1
        
    try:
        from org.python.pydev.debug.ui import JythonUIBridgeInterface  # @UnresolvedImport
        from java.rmi.registry import LocateRegistry  # @UnresolvedImport
        print 'Trying to connect to registry on port ' + str(port+7)
        registry = LocateRegistry.getRegistry(port+7);
        stub = registry.lookup("JythonUIBridge");
                
        REGISTRY['DEBUG'] = stub
        print 'Using native JythonInterpreterBridge ' +repr(stub)
    except:
        print 'Using xmlrpc debug bridge'
        from _pydev_bundle.pydev_imports import xmlrpclib
        
        server = xmlrpclib.Server('http://%s:%s' % (host, port))
        print 'Using port ' + str(port) + ' to connect to SPELL Dev'
        REGISTRY['DEBUG'] = server
except:
    import traceback
    traceback.print_exc()
