################################################################################
#
# NAME              : SPELL Debug Server
# DESCRIPTION       :
#
# FILE              : SPELLDebugServer.py
#
# SPACECRAFT        : A1N, A1M, A2E, A2F, A2G, A3B, A5B, SES06, SES10, SES11, SES12, SES14, SES15, SES16, SES08,SES01,SES02,SES03,AMC21,NSS09
#
# SPECIFICATION     : 
#
# REVISION  HISTORY :
#
# DATE          REV   AUTHOR      DESCRIPTION
# ===========   ===   =========   ==============================================
# 19-JAN-2017   0.1   J.GALL      Initial release. 
# 13-FEB-2017   0.2   J.GALL      Automated start support 
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
def process_command_line(argv):
    """ parses the arguments.
        removes our arguments from the command line """
    setup = {}
    setup['port'] = 0
    i = 0
    del argv[0]
    while (i < len(argv)):
        if argv[i] == '--port':
            del argv[i]
            setup['port'] = int(argv[i])
            del argv[i]
    return setup

Step('INIT','Port initialization')       

if 'PORT' in ARGS.keys():
    port = int(ARGS['PORT'])
else:
    prog_args = sys.argv[:]
    passed_args = process_command_line(prog_args)
    if  passed_args['port'] > 0:  
        port = passed_args['port']
        sys.stdout.write('Starting Debug Server on port ' + str(port))
        Display('Starting Debug Server on port ' + str(port))
    else:
        port = Prompt('Please enter the port that should be used for the Debug Server',NUM)

Step('1','Starting Debug Server')
try:
    import socket
    hostname = socket.gethostname()
    import getpass
    username= getpass.getuser()
    Display('Use this server name to connect to this Debug Server:')
    Display(str(username) + '@' + str(hostname) + '  on port: ' + str(port))
    Display('Remember to use ".scorpio.eng.ses" or ".hifly.eng.ses" as a qualified host name!')
except:
    Display('Could not automatically find out user and host name.',WARNING)
startSPELLDebugServer(int(port))
