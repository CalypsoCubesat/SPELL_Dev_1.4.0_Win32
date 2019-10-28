################################################################################
#
# NAME              : SPELL Debug Server Utils
# DESCRIPTION       :
#
# FILE              : SPELLDebugServerUtils.py
#
# SPACECRAFT        : SES16,SES12,SES14,SES15
#
# SPECIFICATION     : 
#
# REVISION  HISTORY :
#
# DATE          REV   AUTHOR      DESCRIPTION
# ===========   ===   =========   ==============================================
# 19-JAN-2017   0.1   J.GALL      Initial release
################################################################################
#
# This procedure has been developed under STAR3 programs and is based on
# ORBITAL specifications.
#
# You can modify and use this procedure provided that any improvement is shared
# with ORBITAL for the benefit of the STAR3 community.
#
# This procedure is licensed as is. Licensor makes no warranty as to the adequacy
# or suitability of this procedure for purposes required by the Licensee and
# shall not be held liable for the consequences of its use.
#
# LICENSOR DISCLAIMS ALL WARRANTIES EXPRESSED OR IMPLIED INCLUDING WITHOUT
# LIMITATION ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE OR INFRINGEMENT OR VALIDITY.
#
################################################################################
TC_ITEM_PROXY = {}
PTC_ITEM_PROXY = {}
TM_ITEM_PROXY = {}   
def startSPELLDebugServer(port):
        
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    class SPELLDebugServer(object):
        methods = None
        killed = False
        def __init__(self, hostport):
            self.server = SimpleXMLRPCServer(hostport,allow_none=True)
            self.methods = []
        def register_function(self, function, name=None):
            def _function(args, kwargs):
                return function(*args, **kwargs)
            _function.__name__ = function.__name__
            self.methods += [function.__name__]
            self.server.register_function(_function, name)
    
        def serve_forever(self):
            Display('SPELL Debug Server is waiting for connections')
            while not self.killed:
                self.server.handle_request()
            Display('SPELL Debug Server killed.')
        def listMethods(self):
            return self.methods
    server = SPELLDebugServer(("localhost", int(port)))
    server.register_function(server.listMethods,'listMethods')
    import spell.lang.functions as spell_lib
    
    for k,v in spell_lib.__dict__.iteritems():
        if type(v).__name__ == 'function':
            server.register_function(v,k)
        #ENDIF
    #ENDFOR
    from xmlrpclib import Marshaller
    from xmlrpclib import Unmarshaller
    from spell.lib.adapter.result import TmResult
    from spell.lib.adapter.tc_item import TcItemClass
    from spell.lib.adapter.tm_item import TmItemClass
    

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
        global TC_ITEM_PROXY
        write("<value><TcItemClass>")
        h = hash(value)
        TC_ITEM_PROXY[h] = value
        write(str(h))
        write("</TcItemClass></value>\n")
    def create_TcItemClass(self,value):
        global TC_ITEM_PROXY
        self.append(TC_ITEM_PROXY[int(value)])
        
    def dump_TmItemClass(self,value,write):
        global TM_ITEM_PROXY
        write("<value><TmItemClass>")
        h = hash(value)
        TM_ITEM_PROXY[h] = value
        write(str(h))
        write("</TmItemClass></value>\n")    
    def create_TmItemClass(self,value):
        global TM_ITEM_PROXY
        self.append(TM_ITEM_PROXY[int(value)])
    
    FUNCTION_REGISTRY = {}
    
    def dump_function(self,value,write):
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
        if value in FUNCTION_REGISTRY.keys():
            local_function = FUNCTION_REGISTRY[value]
        elif value in globals().keys():
            local_function = globals()[value]
        else:
            return
        self.append(local_function)
        
    Marshaller.dispatch[TmResult] = dump_TmResult
    
    Marshaller.dispatch[TIME] = dump_TIME
    Unmarshaller.dispatch['SPELLTime'] = create_TIME
    
    Marshaller.dispatch[TcItemClass] = dump_TcItemClass
    Unmarshaller.dispatch['TcItemClass'] = create_TcItemClass
    
    Marshaller.dispatch[TmItemClass] = dump_TmItemClass
    Unmarshaller.dispatch['TmItemClass'] = create_TmItemClass
    
    Marshaller.dispatch[type(dump_function)] = dump_function
    Unmarshaller.dispatch['function'] = create_function
    
    Marshaller.dispatch[type(0L)] = lambda _, v, w: w("<value><long>%d</long></value>" % v)
    Unmarshaller.dispatch['long'] = lambda s,v: s.append(long(v))
    try:
        from spell.lib.adapter.tc_item import PtcItemClass
        
        def dump_PtcItemClass(self,value,write):
            global PTC_ITEM_PROXY
            write("<value><PtcItemClass>")
            h = hash(value)
            PTC_ITEM_PROXY[h] = value
            write(str(h))
            write("</PtcItemClass></value>\n")
        def create_PtcItemClass(self,value):
            global PTC_ITEM_PROXY
            self.append(PTC_ITEM_PROXY[int(value)])
        
        Marshaller.dispatch[PtcItemClass] = dump_PtcItemClass
        Unmarshaller.dispatch['PtcItemClass'] = create_PtcItemClass
        
        from spell.lib.adapter.result import PtcResult
        def create_PtcResult(self,value):
            values = value.split('||')
            result = PtcResult()
            result['code']    = eval(values[0])
            result['success'] = eval(values[1])
            result['data']    = eval(values[2])
            result['stage']   = eval(values[3])
            result['error']   = eval(values[4])
            self.append(result)
        Marshaller.dispatch[PtcResult] = lambda _, v, w: w(("<value><PtcResult>%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "%s||"+
                                                                              "</PtcResult></value>") % (repr(v.code()),repr(v.success()),repr(v.data()),repr(v.stage()),repr(v.error()) ))
        Unmarshaller.dispatch['PtcResult'] = create_PtcResult
    except:
        pass
    
    
    def TM_name(self):
        Display('DEBUG:' + repr(self))
        Display('DEBUG:' + str(type(self)))
        Display('DEBUG:' + str(self.name()))
        return self.name()
    def TM_value(self):
        return self.value()
    def TM_time(self):
        return self.time()
    def TM_description(self):
        return self.description()
    def TM_eng(self):
        return self.eng()
    def TM_fullName(self):
        return self.fullName()
    def TM_raw(self):
        return self.raw()
    def TM_status(self):
        return self.status()
    def TM_refresh(self):
        return self.refresh()
    server.register_function(TM_name,'_TM_name')
    server.register_function(TM_value,'_TM_value')
    server.register_function(TM_time,'_TM_time')
    server.register_function(TM_description,'_TM_description')
    server.register_function(TM_eng,'_TM_eng')
    server.register_function(TM_fullName,'_TM_fullName')
    server.register_function(TM_raw,'_TM_raw')
    server.register_function(TM_status,'_TM_status')
    server.register_function(TM_refresh,'_TM_refresh')
    
    
    server.serve_forever()

