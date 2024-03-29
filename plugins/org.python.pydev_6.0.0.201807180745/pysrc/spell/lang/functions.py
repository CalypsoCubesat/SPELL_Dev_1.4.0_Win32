###############################################################################
"""
Date: 01/07/2008

Project: SPELL

Description
===========

Definition of all USL language user functions

Authoring
=========

@organization: SES ENGINEERING

@copyright: Copyright (C) 2008, 2015 SES ENGINEERING, Luxembourg S.A.R.L.
            
@license:  This file is part of SPELL.

 This library is free software: you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation, either
 version 3 of the License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License and GNU General Public License (to which the GNU Lesser
 General Public License refers) along with this library.
 If not, see <http://www.gnu.org/licenses/>.
 
@version: 1.0
@requires: Python 2.5.x
"""
###############################################################################

#===============================================================================
# SPELL imports
#===============================================================================
from spell.utils.log import *
from spell.lang.constants import *
from spell.lang.modifiers import *
from spell.lib.exception import *
from spell.lib.adapter.utctime import *
from spell.lib.registry import *
from spell.lib.adapter.expression import Expression,AND_TYPE,OR_TYPE

#===============================================================================
# Local imports
#===============================================================================

#===============================================================================
# System imports
#===============================================================================
import time,os,string


#==============================================================================
def Abort( message = "Execution Aborted" ):
    """
    Aborts the procedure execution.
    
    Syntax 1:
    =========
    
    To abort the procedure showing the message 'Procedure aborted'::
    
        Abort()

        
    Syntax 2:
    =========
    
    To abort the procedure showing the given message in the GUI display::
         
        Abort( message )
        
    Result:
    =======
    
    This function does not return a value.
    """
    
    # Abort the executor
    if REGISTRY.exists('EXEC'):
        REGISTRY['EXEC'].abort(message)

#==============================================================================
def DisplayStep( id, description ):
    """
    Change the current step description. Not valid for goto targets.
    
    Result:
    =======
    
    This function does not return a value.
    """
    
    # Abort the executor
    if REGISTRY.exists('EXEC'):
        REGISTRY['EXEC'].setStep(id,description)

#==============================================================================
def Finish( message = "Completed Execution" ):
    """
    Finishes the procedure execution.
    
    Syntax 1:
    =========
    
    To finish the procedure showing the message 'Procedure finished by user'::
    
        Finish()

        
    Syntax 2:
    =========
    
    To finish the procedure showing the given message in the GUI display::
         
        Finish( message )
        
    Result:
    =======
    
    This function does not return a value.
    """
    
    # Cleanup the executor
    if REGISTRY.exists('EXEC'):
        REGISTRY['EXEC'].finish(message)

#==============================================================================
def Prompt( *args, **kargs ):
    """
    Prompt the user for confirmation or obtaining data.
    
    Syntax 1:
    =========

    Show the given message to the user and expect a OK/CANCEL answer. Used 
    for basic confirmation messages::
    
        <result> = Prompt( message )
    
    Syntax 2:
    =========

    Ask the user for information using the given configuration for the prompt. 
    The configuration dictionary determines the type and behavior of the prompt. 
    Possible configuration::
                
        <result> = Prompt( message, {<modifiers>}, <modifiers> )
        
    See the 'Modifiers' section below for the list of modifiers or parameters 
    that can be used.
            
    Syntax 3
    ========

    Prompt the user for choosing one of the given options. The configuration 
    dictionary determines the behavior of the prompt. Providing the modifier
    C{Type:LIST} or one of this variations is mandatory::
                
        <result> = Prompt( message, [ <options> ], {Type:LIST, <modifiers>}, <modifiers> )
        <result> = Prompt( message, [ <options> ], {<modifiers>}, <modifiers>, type = LIST  )
        
    See the 'Option Lists' section below for details about option lists.
        
    Modifiers
    =========    
        
        1. Type - Used for choosing the type of prompt. Possible values::
        
            - OK:             the user may choose 'OK' only
            - CANCEL:         the user may choose 'Cancel' only
            - OK_CANCEL:      the user may choose 'OK' or 'Cancel'
            - YES:            the user may choose 'Yes' only
            - NO:             the user may choose 'No' only
            - YES_NO:         the user may choose 'Yes' or 'No'
            - ALPHA:          the user shall give an alphanumeric answer
            - NUM:            the user shall give a numeric answer
            - DATE:           the user shall give a date/time string
            
            - LIST:           the user shall select between the given list of
                              options. Options shall be provided in the form
                              'Key:Text' or 'Text'. If the former is used, the 
                              prompt result is the selected key. If the latter
                              is used, the prompt result is the index of the option.
                              
            - LIST | NUM:     the user shall select between the given list of
                              options. Options shall be provided in the form
                              'Key:Text' or 'Text'. The prompt result is the 
                              option Text casted to a number.
                              
            - LIST | ALPHA:   the user shall select between the given list of
                              options. Options shall be provided in the form
                              'Key:Text' or 'Text'. The prompt result is the 
                              option text.

            - LIST | COMBO:   use a drop-down list to show the options. 
                                
            Default is Type:OK
    
        2. ValueType - Used for forcing the return type of the prompt. 
           Possible values::
         
            - LONG:           force the cast of the answer to long integer
            - FLOAT:          force the cast of the answer to float
            - STRING:         force the cast of the answer to string
            - BOOLEAN:        force the cast of the answer to boolean.
            - DATETIME:       force the cast of the answer to date-time type.

            Default is ValueType:STRING.            
            
        3. Timeout:<float> - Timeout in seconds for obtaining an answer from the user. It shall be used 
           with Default modifier. Default is 30.0 seconds.
                                        
        4. Default:<answer> - Default answer proposed to the user. Also returned if there is a timeout.
           There is no default for prompt answer.
        
    Option Lists
    ============
                                            
    The format of the option list is the following::
    
        [ 'Key1:Text1', 'Key2:Text2', ... ]
        
    or::

        [ 'Text1', 'Text2', ... ]
        
    As it has been said, if the first format is used the result of the prompt
    will be the option Key unless one of the combinations LIST | NUM or LIST | ALPHA
    is used, in such cases the option text or the casted option text is returned.
    
    On the other hand, when using the second format, the result of the prompt
    will be the option index, unless one of the combinations LIST | NUM or LIST | ALPHA
    is used, in such cases the option text or the casted option text is returned.
    
    Result:
    =======
    
    The return value of the prompt function depends on the prompt type and on
    the usage of the ValueType modifier. 
    """
    from helpers.genhelper import Prompt_Helper
    helper = Prompt_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
def Display( *args, **kargs ):
    """
    Prompts the user for information
    
    Syntax 1:
    =========
        
    Display the given message as INFORMATION::
            
        Display( message )
        
    Syntax 2:
    =========
    
    Display a message using specific configuration. See the 'Modifiers' section
    below for a list of the possible modifiers for this function::
                
        Display( message, {<modifiers>}, <modifiers> )
        
    Modifiers:
    ==========
    
        1. Type - Determines the way the message is displayed on the GUI::
        
            - DISPLAY:          Normal display message
            - LOGMSG:           Message will be shown in log only
            - DIALOG:           Message will be shown in a dialog
            
           Default is Type:DISPLAY
            
        2. Severity - Determines the severity of the message::
        
            - INFORMATION:      Information message
            - WARNING:          Warning message
            - ERROR:            Error message
            - FATAL:            Fatal error message

           Default is Severity:INFORMATION
        
    Result:
    =======
    
    This function does not return a value.
    """
    from helpers.genhelper import Display_Helper
    helper = Display_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def Notification( *args, **kargs ):
    """
    Send item notifications
    This function does not return a value.
    """
    from helpers.genhelper import Notification_Helper
    helper = Notification_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def Event( *args, **kargs ):
    """
    Inject an event into the controlled system.
    
    Syntax 1:
    =========
                
    Inject an event with severity INFORMATION and scope SCOPE_PROC::
    
        Event( message )

    Syntax 2:
    =========
                
    Display a message using specific configuration:: 

        Event( message, {<modifiers>}, <modifiers> )
        
        
    Modifiers:
    ==========
    
    The possible modifiers for this function are:
         
        1. Severity - Determines the severity of the event::
        
            - INFORMATION:     Information message
            - WARNING:         Warning message
            - ERROR:           Error message
            - FATAL:           Fatal error message

           Default is Severity:INFORMATION

        2. Scope - Determines the scope of the event::
        
            - SCOPE_PROC:      Procedure-related
            - SCOPE_SYS:       Controlled system scope
            - SCOPE_CFG:       Configuration-related

           Default is Scope:SCOPE_PROC
                    
    Result:
    =======
    
    This function does not return a value.
    """
    from helpers.evhelper import Event_Helper
    helper = Event_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetTM( *args, **kargs ):
    """
    Obtain the value of a TM parameter.
    
    Syntax 1:
    =========
                
    Obtain the default value of the given TM parameter (name or item) using
    default configuration of the TM interface::
        
        <value> = GetTM( <tm item>|'tm name' )
        
    The argument may be a tm item instance or the name of a TM parameter.

    Syntax 2:
    =========

    Obtain the TM parameter value with specific configuration::
                
        <value> = GetTM( <tm item>|'tm name', {<modifiers>}, <modifiers> )
        
    Modifiers:
    ==========
    
    Possible modifiers for this function are:
        
        1. ValueFormat - Determines the TM value to be used::
        
            - RAW: Use raw value. 
            - ENG: Use engineering or calibrated value. 
            - DEF: Use default value  
            
            Default is ValueFormat:ENG            
        
        2. Wait - If True, wait for the next parameter update. Otherwise
           return the last recorded value:: 

            - True: Wait until the next parameter update arrives and return it. 
            - False: Provide the last recorded value inmediately.
            
            Default is Wait:False.
            
        3. Timeout:<float> - Applies only if Wait is True. Sets the time limit 
           for the next parameter update. Default is 3.0 seconds.
                                            
        4. OnFailure - Determines the list of choices shown to the user in case 
           of a failure. It can be a combination ('|')  of the values shown below:: 
                   
            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement.
            - REPEAT:      The TM check has to be repeated.

            Default is ABORT | SKIP | REPEAT | CANCEL.
                    
    Result:
    =======
    
    The value of the given TM parameter.
    """
    from helpers.tmhelper import GetTM_Helper
    helper = GetTM_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def Verify( *args, **kargs ):
    """
    Perform a TM verification. Return True if the verification is 
    successful, False otherwise.
    
    Syntax 1:
    =========

    Perform a TM verification set::

        True/False = Verify( [ verify list ], <comparison>, <value> )
        
    The given verification list shall have this format::    
    
        [ [ <tm_item>, <comparison>, <value>, {modifiers} ], ... ]
        [ [ <tm_item>, <binary comparison>, <value1>, <value2>, {modifiers} ], ... ]
        
    Where the modifier dictionary is optional. Modifiers may be used to determine 
    the way the tm item value is extracted, for example.

    A TM item instance or a TM parameter name may be passed as the main argument.
    The <value> argument may be a variable, constant or another TM item. The
    <comparison> argument is the comparison operator. See the 'Comparisons' 
    section below for a list of the possible comparison operators.
        
    Modifiers:
    ==========   
    
    Possible modifiers for this function are:
    
        1. ValueFormat - Determines the TM value to be used:: 
        
            - RAW: Use raw value. 
            - ENG: Use engineering or calibrated value. 
            - DEF: Use default value  
            
            Default is ValueFormat:ENG
        
        2. Wait - If True, wait for the next parameter update. Otherwise
           return the last recorded value::

            - True: Wait until the next parameter update arrives and return it. 
            - False: Provide the last recorded value inmediately.
            
            Default is Wait:False.
            
        3. Timeout:<float> - Applies only if Wait is True. Sets the time limit 
           for the next parameter update. Default is 3.0 seconds.
                                            
        4. OnFailure - Determines the list of choices shown to the user in case 
           of a failure. It can be a combination ('|')  of the values shown below:: 
                   
            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement and the function returns True
            - CANCEL:      The user may skip this statement and the function returns False
            - REPEAT:      The TM check has to be repeated.
            
            Default is ABORT | SKIP | REPEAT | CANCEL.

        5. Tolerance:<float> - Tolerance to be used in comparisons. No default.

        6. Retries:<int> - Number of times that the comparison should be repeated
           whenever it fails, before actually declaring the operation as failed.
           Default is 2.

        7. Delay:<int/float/time> - Time to wait before starting the verification.

    Comparisons:
    ============
    
    The following comparison operators may be used:
    
        1. eq - The TM parameter value shall be equal to the given value or TM item value.
        2. neq - The TM parameter value shall be different from the given value or TM item value.
        3. lt - The TM parameter value shall be less than the given value or TM item value.
        4. gt - The TM parameter value shall be greater than the given value or TM item value.
        5. le - The TM parameter value shall be less than or equal to the given value or TM item value.
        6. ge - The TM parameter value shall be greather than or equal to the given value or TM item value.
        7. bw - The TM parameter value shall be between the two given values or TM items.
        8. nbw - The TM parameter value shall not be between the two given values or TM items.
        
    Result:
    =======
    
    True if the verification(s) is(are) successful, or if there is a failure and
    the user chooses SKIP. False if the verification fails or the user chooses CANCEL.
    """
    return True
    
    from helpers.tmhelper import Verify_Helper
    helper = Verify_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def WaitFor( *args, **kargs ):
    """
    Wait until a given condition is satisfied.
    
    Syntax 1:
    =========
    
    Wait until the given TM parameter value satisfies the given condition::

        True/False = WaitFor( [verification list], Delay=<TIME>, <modifiers> )

    The condition shall be fullfilled before the relative time specified with Delay.
    The verification list follows the same syntax as for Verify function.
    See 'Modifiers' section below for a list of the possible modifiers for this function.
        
    Syntax 2:
    =========
    
    Wait for the given amount of time. <time> shall be a number, a date/time string
    (defining a relative time) or a relative TIME instance::
    
        True/False = WaitFor( <time>, <modifiers> )
        True/False = WaitFor( Delay=<time>, <modifiers> )
        
    Syntax 2:
    =========
    
    Wait until the given date/time. <time> shall be a date/time string
    (defining an absolute time) or an absolute TIME instance::
    
        True/False = WaitFor( Until=<time>, <modifiers> )
        True/False = WaitFor( Delay=<time>, <modifiers> )
        
        
    Modifiers:
    ==========   
    
    Possible modifiers for this function are:
    
        1. ValueFormat - Determines the TM value to be used::
        
            - RAW: Use raw value. 
            - ENG: Use engineering or calibrated value. 
            - DEF: Use default value  
            
            Default is ValueFormat:ENG
        
        2. Timeout:<float> - Applies only if Wait is True. Sets the time limit 
           for the next parameter update. Default is 3.0 seconds.
                                            
        3. OnFailure - Determines the list of choices shown to the user in case 
           of a failure. It can be a combination ('|')  of the values shown below:: 

            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement and the function returns True
            - CANCEL:      The user may skip this statement and the function returns False
            - REPEAT:      The TM check has to be repeated.

           Default is ABORT | SKIP | REPEAT | CANCEL.        

        4. Tolerance:<float> - Tolerance to be used in comparisons. No default.

        5. Interval:<int/float/TIME> - Update a time condition status using the given numer as period
        
        6. Interval:[list] - List of int/float/TIME. Update a time condition status 
           using an incremental notification interval. The list shall contain a decreasing set of
           times, e.g. [20*MINUTE,5*MINUTE,MINUTE]. In this example, the condition
           status will be updated: 
              
                (1) When the time limit is 20 minutes far,
                (2) Once each 5 minutes after (1),
                (3) When the time limit is 5 minutes far,
                (4) Once per minute after (3)
        
        7. Message:<string> - Message to be shown when a time condition is updated.
        
    Result:
    =======
    
    True if the condition checks works normally, False if there is a failure (and
    SKIP is not selected) or there is a wait timeout.
        
    """
    # TODO
    return True

    from helpers.genhelper import WaitFor_Helper
    helper = WaitFor_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def Pause( *args, **kargs ):
    """
    Set the procedure status to paused. 
    
    Syntax 1:
    =========

    Set the procedure status to paused inmediately::
    
        Pause()
        
    Syntax 2:
    =========
    
    Set the procedure status to paused if the given condition is satisfied::
    
        True/False = Pause( [verification list], <modifiers> )
        
    The verification list follows the same syntax as for Verify function.

    Modifiers:
    ==========   
    
    Possible modifiers for this function are:
    
        1. ValueFormat - Determines the TM value to be used::
        
            - RAW: Use raw value. 
            - ENG: Use engineering or calibrated value. 
            - DEF: Use default value  
            
            Default is ValueFormat:ENG
        
        2. Timeout:<float> - Applies only if Wait is True. Sets the time limit 
           for the next parameter update. Default is 3.0 seconds.
                                            
        3. OnFailure - Determines the list of choices shown to the user in case 
           of a failure. It can be a combination ('|')  of the values shown below:: 

            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement and the function returns True
            - CANCEL:      The user may skip this statement and the function returns False
            - REPEAT:      The TM check has to be repeated.

           Default is ABORT | SKIP | REPEAT | CANCEL.        

        4. Tolerance:<float> - Tolerance to be used in comparisons. No default.
        
    Result:
    =======
    
    False if there is a failure (and SKIP is not selected) or the conditions
    are not fulfilled, True otherwise.
    """
    # TODO
    return True

    from helpers.exechelper import Pause_Helper
    helper = Pause_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )


#==============================================================================
def Send( *args, **kargs ):
    """
    Send a command/sequence or group of command/sequences from the GCS. 
    
    Syntax 1:
    =========

    Send the given item with no arguments. If an item instance is passed, the 
    item may contain arguments. If only the item name is passed (as a string), 
    no arguments can be used::
    
        True/False = Send( command = <tc item>|'tc item', <modifiers> )
        True/False = Send( sequence = <tc item>|'tc item', <modifiers> )
        True/False = Send( group = [<tc item>|'tc item',<tc item>|'tc item'], <modifiers> )

    Notice that the nature of the item to be sent is determined by the keywords
    'command', 'sequence' or 'group', being the last one the identification
    for a list of individual commands or sequences. 
    
    See section 'Modifiers' below to see a list of the possible modifiers for this function.
        
    Syntax 2:
    =========
    
    Send the given item with arguments. Arguments can be specified either inside
    the passed tc item, either using the 'args' keyword argument. The recommended
    option is always to pass the arguments inside the tc item. This argument
    assignment can be easily done by using the function BuildTC.::
    
        True/False = Send( command = <tc item>|'tc item', args = [arg list] )
        True/False = Send( sequence = <tc item>|'tc item', args = [arg list]  )
        True/False = Send( group = [<tc item>|'tc item',<tc item>|'tc item'] )
    
    Notice that the 'args' keyword argument cannot be used with groups. The format
    of the argument list is::
    
        [ [ <arg name>, <arg value>, {modifiers} ], ... ] 
    
    Possible modifiers for tc arguments are::
        
        ValueType: LONG,SHORT,STRING,BOOLEAN,TIME,FLOAT     (Default: LONG)
        ValueFormat: ENG/RAW/DEF                            (Default: ENG)
        Radix: DEC/HEX/OCT                                  (Default: DEC) 
        Units: <string>                                     (Default: "")
             
    Syntax 3:
    =========
    
    Send the given item and perform a closed-loop TM verficiation afterwards::
    
          True/False = Send( command = <tc item>|'tc item', 
                             args = [arg list],
                             verify= [tm conditions] )
            
    Refer to Verify function help to see a description of the modifiers applicable
    to the TM conditions and their syntax.
       
    Modifiers:
    ==========
    
        1. Time:<TIME/datetime string> - Timetag the command with the given time.
           No default value.
        
        2. Timeout:<float> - Sets the time limit for command execution confirmation. 
           Default is 10.0 seconds.
                                            
        3. OnFailure - Determines the list of choices shown to the user in case 
           of a failure. It can be a combination ('|')  of the values shown below:: 

            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement and the function returns True
            - CANCEL:      The user may skip this statement and the function returns False
            - RECHECK:     Repeat the TM verification but not resend the command.
            - RESEND:      The command has to be sent again.

           Default is ABORT | SKIP | RESEND | CANCEL.        

        4. Confirm:True/False - Prompt the user for confirmation before sending 
           the command. Default is False.

        5. addInfo:"" - Dictionary of string values used to configure the 
           driver at the moment of the command injection. The contents
           of this modifier are completely spacecraft-dependent.

        6. Delay:<seconds> - Time to wait between the command/sequence execution
                             confirmation and the TM verifications. Default is 0.

        7. AdjLimits:True/False - If True and TM conditions are given, the OOL
                                  definitions of the TM parameters will be adjusted.

    Result:
    =======
    
    True if the command was sent successfully or the user chooses SKIP. False
    otherwise.

    """
    # TODO
    #return True

    from helpers.tchelper import Send_Helper
    helper = Send_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
# Backwards compatibility
SendAndVerify = Send
SendAndVerifyAdjLim = Send

#==============================================================================
def BuildTC( *args, **kargs ):
    """
    Construct a TC item
    
    Syntax 1:
    =========
    
    <tc item> = BuildTC( 'TC name', args = [arg list] )
    
    The format of the argument list is::
    
        [ [ <arg name>, <arg value>, {modifiers} ], ... ] 
    
    Possible modifiers for tc arguments are::
        
        ValueType: LONG,SHORT,STRING,BOOLEAN,TIME,FLOAT     (Default: LONG)
        ValueFormat: ENG/RAW/DEF                            (Default: ENG)
        Radix: DEC/HEX/OCT                                  (Default: DEC) 
        Units: <string>                                     (Default: "")    
    
    Modifiers:
    ==========
    
        None.
    
    Return:
    =======
    """
    from helpers.tchelper import BuildTC_Helper
    helper = BuildTC_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
def BuildPTC( *args, **kargs ):
    """
    Construct a pseudo TC item
    
    Syntax 1:
    =========
    
    <ptc item> = BuildPTC( 'TC name', args = [arg list] )
    
    The format of the argument list is::
    
        [ [ <arg name>, <arg value>, {modifiers} ], ... ] 
    
    Possible modifiers for tc arguments are::
        
        ValueType: LONG,SHORT,STRING,BOOLEAN,TIME,FLOAT     (Default: LONG)
        ValueFormat: ENG/RAW/DEF                            (Default: ENG)
        Radix: DEC/HEX/OCT                                  (Default: DEC) 
        Units: <string>                                     (Default: "")    
    
    Modifiers:
    ==========
    
        None.
    
    Return:
    =======
    """
    return True
#==============================================================================
def SetGroundParameter( *args, **kargs ):
    """
    Inject a ground parameter value.
    
    Syntax 1:
    =========
    
    To inject a single ground parameter::
    
        SetGroundParameter( <tm_item>|'tm item', <value>, {modifiers} )
    
    The TM item name or instance may be given.

    Syntax 2:
    =========
    
    To inject several ground parameters::
    
        SetGroundParameter( [...], {modifiers} )
    
    Where the list format is the following::
    
        [ [ <tm_item>|'tm item', <value>, {modifiers} ], [...], ... ]
    
    Modifiers can be used for each parameter in order to specify the injected value
    format, radix, units etc.
    
    Modifiers:
    ==========
    
        1. ValueFormat - Determines the TM value to be used::
        
            - RAW: Use raw value. 
            - ENG: Use engineering or calibrated value. 
            - DEF: Use default value  
            
            Default is ValueFormat:ENG

        2. ValueType - Used for forcing the return type of the prompt. 
           Possible values::
         
            - LONG:           force the cast of the answer to long integer
            - FLOAT:          force the cast of the answer to float
            - STRING:         force the cast of the answer to string
            - DATE:           force the cast of the answer to date-time type
            - BOOLEAN:        force the cast of the answer to boolean.

            Default is ValueType:STRING.            
                            
        3. OnFailure - the following actions can be used::
                        
            - ABORT:       The user may abort the procedure.
            - SKIP:        The user may skip this statement, the function returns True
            - CANCEL:      The user may skip this statement, the functions returns False
            - REPEAT:      Repeat the TM injection.

            Default is ABORT | SKIP | REPEAT | CANCEL.        

        4. Radix: determines the radix of the value::
        
            - HEX: hexadecimal
            - DEC: decimal
            - OCT: octal
            - BIN: binary
        
    Return:
    =======
    
    True if the operation is successful, False otherwise. In case of failure,
    if the user selects SKIP the result is True, if CANCEL is selected the
    result is False.
    """
    from helpers.tmhelper import SetGroundParameter_Helper
    helper = SetGroundParameter_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetResource( *args, **kargs ):
    """
    Set a configuration value on the controlled system
    
    Syntax 1:
    =========
    
    To modify a configuration value of the controlled system::
    
        True/False = SetResource( <resource name>, <resource value> ) 
    
    Modifiers:
    ==========
    
        None.
    
    Return:
    =======
    
    True if the operation is successful, False otherwise.
    """
    from helpers.rschelper import SetResource_Helper
    helper = SetResource_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetResource( *args, **kargs ):
    """
    Get a configuration value from the controlled system
    
    Syntax 1:
    =========
    
    To obtain a configuration value of the controlled system::
    
        <value> = GetResource( <resource name> ) 
    
    Modifiers:
    ==========
    
        None.
    
    Return:
    =======
    
    The resource value.
    """
    from helpers.rschelper import GetResource_Helper
    helper = GetResource_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetLink( *args, **kargs ):
    """
    Change a link status on the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.rschelper import SetLink_Helper
    helper = SetLink_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def CheckLink( *args, **kargs ):
    """
    Check a link status on the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.rschelper import CheckLink_Helper
    helper = CheckLink_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def StartTask( *args, **kargs ):
    """
    Start a task on the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.tskhelper import StartTask_Helper
    helper = StartTask_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def StopTask( *args, **kargs ):
    """
    Stop a task on the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.tskhelper import StopTask_Helper
    helper = StopTask_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def UserLogin( *args, **kargs ):
    """
    Login on the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.usrhelper import UserLogin_Helper
    helper = UserLogin_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def UserLogout( *args, **kargs ):
    """
    Logout from the controlled system
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.usrhelper import UserLogout_Helper
    helper = UserLogout_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def StartProc( *args, **kargs ):
    """
    Start a sub-procedure.
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    # TODO
    return True

    from helpers.tskhelper import StartProc_Helper
    helper = StartProc_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
def SetExecDelay( *args, **kargs ):
    """
    Modify the execution delay between SPELL statements.
    
    Syntax 1:
    =========
    
        True/False = SetExecDelay( <delay> )
        
    Where <delay> may be any float or integer number.

    Modifiers:
    ==========
    
    None.
    
    Return:
    =======
    
    True if the operation is successful, False otherwise.
    """
    from helpers.exechelper import SetExecDelay_Helper
    helper = SetExecDelay_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def ShowText( *args, **kargs ):
    """
    Show a text banner on the GUI.
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    Display("NOT IMPLEMENTED",WARNING)
    return True

#==============================================================================
def GetTMparam( *args, **kargs ):
    """
    Get a TM parameter property.
    """
    from helpers.tmhelper import GetTMparam_Helper
    helper = GetTMparam_Helper()
    helper.configure(*args, **kargs)
    return helper.execute(*args, **kargs)

#==============================================================================
def SetTMparam( *args, **kargs ):
    """
    Set a TM parameter property.
    """
    from helpers.tmhelper import SetTMparam_Helper
    helper = SetTMparam_Helper()
    helper.configure(*args, **kargs)
    return helper.execute(*args, **kargs)
    
#==============================================================================
def GetLimits( *args, **kargs ):
    """
    Get a TM parameter property.
    
    Syntax 1:
    =========
    
       <value> = GetLimits( <tm item/name>, [LoRed|LoYel|HiRed,HiYel] )

    Syntax 2:
    =========
    
       [<value>,<value>] = GetLimits( <tm item/name>, [LoBoth|HiBoth] )

    Syntax 3:
    =========
    
       [<value>,<value>,<value>,<value>] = GetLimits( <tm item/name> )
    
    Modifiers:
    ==========
    
    Return:
    =======
    
    The limit value(s)
    """
    from helpers.tmhelper import GetLimits_Helper
    helper = GetLimits_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetLimits( *args, **kargs ):
    """
    Set a TM parameter property.
    
    Syntax 1:
    =========
    
    Set the alarm limits configuration for the given TM parameter, setting both
    Low-Yellow and Low-Red limits to same value, High-Yellow and High-Red to 
    same value::
        
        <True/False> = SetTMparam( <tm item/name>, Limits = [ <Low>, <High> ] )
        <True/False> = SetTMparam( <tm item/name>, LoBoth = <Low>, HiBoth=<High>  )
        
    Syntax 2:
    =========
    
    Set the alarm limits configuration for the given TM parameter, setting 
    different values for Low-Yellow, Low-Red, High-Yellow and High-Red::
        
        <True/False> = SetTMparam( <tm item/name>, Limits = [ <LoRed>, <LoYel>, <HiRed>, <HiYel> ] )
        <True/False> = SetTMparam( <tm item/name>, LoRed=<LoRed>, LoYel=<LoYel>, HiRed=<HiRed>, HiYel=<HiYel> )

    Syntax 3:
    =========
    
    Set the alarm limits configuration for the given TM parameter, setting 
    values for the given modifiers only::
        
        <True/False> = SetTMparam( <tm item/name>, LoRed<LoRed> )

    Syntax 4:
    =========
    
    Set the alarm limits configuration for the given TM parameter, using
    a midpoint value and a tolerance::
        
        <True/False> = SetTMparam( <tm item/name>, Midpoint=<Center>, Tolerance=<Value> )

    Return:
    =======
    
    True if the operation is successful.
    """
    from helpers.tmhelper import SetLimits_Helper
    helper = SetLimits_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def LoadLimits( *args, **kargs ):
    """
    Load a set of limit definitions from a URL into the GCS
    
    Syntax 1:
    =========
    
        <True/False> = LoadLimits( "limits://filename" )
    
    Return:
    =======
    
    True if the operation is successful.
    """
    from helpers.tmhelper import LoadLimits_Helper
    helper = LoadLimits_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def RestoreNormalLimits( *args, **kargs ):
    """
    Reset temporary limit definitions in the GCS
    
    Syntax 1:
    =========
    
        <True/False> = ResetLimits()
    
    Return:
    =======
    
    True if the operation is successful.
    """
    from helpers.tmhelper import RestoreNormalLimits_Helper
    helper = RestoreNormalLimits_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def DisableAlarm( *args, **kargs ):
    """
    Disable OOL for the given list of TM parameters.
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    Display("Cannot disable alarm: not implemented", Severity = WARNING )
    return True

#==============================================================================
def EnableAlarm( *args, **kargs ):
    """
    Enable the OOL for the given list of TM parameters.
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    Display("Cannot enable alarm: not implemented", Severity = WARNING )
    return True

#==============================================================================
def LoadDictionary( *args, **kargs ):
    """
    Load a key/value dictionary database.
    
    Syntax 1:
    =========
    
    Load a key/value database or dictionary from the specified location::
    
        <dictionary> = LoadDictionary( "file://Filename" )
        <dictionary> = LoadDictionary( "sqlite://DatabaseName" )
        <dictionary> = LoadDictionary( "sql://DatabaseName" )

    Syntax 2:
    =========
    
    Load a key/value database of a predefined type. The predefined database
    types are 'mmd', standing for Maneuvre Message Database, 'scdb' for
    'Spacecraft Database' and 'gdb' for "Ground Database"::
    
        <dictionary> = LoadDictionary( "mmd://Filename" )
        <dictionary> = LoadDictionary( "scdb://DatabaseName" )
        
    Modifiers:
    ==========
    
    None applicable.
    
    Return:
    =======
    
    The corresponding database object.
    
    """
    from helpers.filehelper import LoadDictionary_Helper
    helper = LoadDictionary_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SaveDictionary( *args, **kargs ):
    """
    Save a key/value dictionary database.
    
    Syntax:
    =========
    
    Save a key/value database previously loaded with LoadDictionary 
    or created with CreateDictionary::
    
        SaveDictionary( <dictionary> )

    Modifiers:
    ==========
    
    None applicable.
    
    Return:
    =======
    
    None.
    
    """
    from helpers.filehelper import SaveDictionary_Helper
    helper = SaveDictionary_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def CreateDictionary( *args, **kargs ):
    """
    Creates/overrides an empty key/value dictionary database with the provided URL.
    An URL uses the pattern "<type>://<location>", e.g.: "usr://mydb".
    
    Syntax:
    =========
    
    Create a key/value database::
    
        <dictionary> = CreateDictionary( <URL> )

    Modifiers:
    ==========
    
    None applicable.
    
    Return:
    =======
    
    The newly created database object.
    
    """
    from helpers.filehelper import CreateDictionary_Helper
    helper = CreateDictionary_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def AdjustLimits( *args, **kargs ):
    """
    Adjust OOL definitions on the given parameter(s) using the given tolerances
    
    Syntax 1:
    =========
    
    Modifiers:
    ==========
    
    Return:
    =======
    """
    from helpers.limhelper import AdjustLimits_Helper
    helper = AdjustLimits_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def OpenDisplay( *args, **kargs ):
    """
    Open a GCS display
    
    Syntax 1:
    =========
    
    True/False = OpenDisplay( <display name>, <modifiers> )
    
    Modifiers:
    ==========
    
        1. Host: host where the display should be open. 
        
            Default is localhost.
    
    Return:
    =======
    
    True on success.
    """
    from helpers.tskhelper import OpenDisplay_Helper
    helper = OpenDisplay_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def CloseDisplay( *args, **kargs ):
    """
    Close a GCS display
    
    Syntax 1:
    =========
    
    True/False = CloseDisplay( <display name>, <modifiers> )
    
    Modifiers:
    ==========
    
        1. Host: host where the display should be closed. 
        
            Default is localhost.
    
    Return:
    =======
    
    True on success.
    """
    from helpers.tskhelper import CloseDisplay_Helper
    helper = CloseDisplay_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def PrintDisplay( *args, **kargs ):
    """
    Prints a GCS display
    
    Syntax 1:
    =========
    
    True/False = PrintDisplay( <display name>, <modifiers> )
    
    Modifiers:
    ==========
    
        1. Printer - Determines the printer to be used::
        
            - "Printer name": The printer name as a string 
            
            Default is empty. If this modifier is not provided, the display
            is printed to a file.
            
        2. Format - Determines the format of the printout::
        
            - "ps": Print to postscript
            - "jpg": Print to jpg
            - "png": Print to png
            - "vector": Print to plain text
            - "matrix": Print to plain text in table mode
        
        3. Host: host where the display should be open/printed. 
        
            Default is localhost.
    
    Return:
    =======
    
    True on success.
    """
    from helpers.tskhelper import PrintDisplay_Helper
    helper = PrintDisplay_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def Script( *args, **kargs ):
    """
    Execute a given script (source code)
    
    Syntax 1:
    =========
    
    Execute the given piece of source code::
    
        True/False = Script("my SPELL code")
    
    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    True on success, False on failure
    """
    from helpers.exechelper import Script_Helper
    helper = Script_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def ChangeLanguageConfig( *args, **kargs ):
    """
    Modify the defaults for a given language interface or function
    
    Syntax 1:
    =========
    
    Change a default value for the (e.g.) TM interface::
    
        ChangeLanguageConfig( TM, Wait = False )

    Syntax 2:
    =========
    
    Change a default value for the (e.g.) Send function::
    
        ChangeLanguageConfig( Send, Delay = 3 )
    
    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.genhelper import ChangeLanguageConfig_Helper
    helper = ChangeLanguageConfig_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetLanguageConfig( *args, **kargs ):
    """
    Modify the defaults for a given language interface or function
    
    Syntax 1:
    =========
    
    Change a default value for the (e.g.) TM interface::
    
        ChangeLanguageConfig( TM, Wait = False )

    Syntax 2:
    =========
    
    Change a default value for the (e.g.) Send function::
    
        ChangeLanguageConfig( Send, Delay = 3 )
    
    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.genhelper import GetLanguageConfig_Helper
    helper = GetLanguageConfig_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetUserAction( *args, **kargs ):
    """
    Associate a procedure function to an action which can be triggered by the user
    
    Syntax 1:
    =========
    
        SetUserAction( <function>, "label" )

    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.exechelper import SetUserAction_Helper
    helper = SetUserAction_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def EnableUserAction( *args, **kargs ):
    """
    Enable user action
    
    Syntax 1:
    =========
    
        EnableUserAction()

    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.exechelper import EnableUserAction_Helper
    helper = EnableUserAction_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def DisableUserAction( *args, **kargs ):
    """
    Disable user action
    
    Syntax 1:
    =========
    
        DisableUserAction()

    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.exechelper import DisableUserAction_Helper
    helper = DisableUserAction_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def DismissUserAction( *args, **kargs ):
    """
    Dismiss user action
    
    Syntax 1:
    =========
    
        DismissUserAction()

    Modifiers:
    ==========
    
    None
    
    Return:
    =======
    
    None
    """
    from helpers.exechelper import DismissUserAction_Helper
    helper = DismissUserAction_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def bin( number, count = 24 ):
    """
    Convert an integer 'number' to binary representation, using 'count' number of digits
    """
    return "".join([str((number >> y) & 1) for y in range(count-1, -1, -1)])

#==============================================================================
def OpenFile( *args, **kargs ):
    from helpers.filehelper import OpenFile_Helper
    helper = OpenFile_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
def WriteFile( *args, **kargs ):
    from helpers.filehelper import WriteFile_Helper
    helper = WriteFile_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
def CloseFile( *args, **kargs ):
    from helpers.filehelper import CloseFile_Helper
    helper = CloseFile_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )
    
#==============================================================================
def ReadFile( *args, **kargs ):
    from helpers.filehelper import ReadFile_Helper
    helper = ReadFile_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def DeleteFile( *args, **kargs ): 
    from helpers.filehelper import DeleteFile_Helper
    helper = DeleteFile_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def ReadDirectory( *args, **kargs ):
    from helpers.filehelper import ReadDirectory_Helper 
    helper = ReadDirectory_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetSharedData ( *args, **kargs ):
    from helpers.datahelper import SetSharedData_Helper
    helper = SetSharedData_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetSharedData ( *args, **kargs ):
    from helpers.datahelper import GetSharedData_Helper
    helper = GetSharedData_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetSharedDataKeys ( *args, **kargs ):
    from helpers.datahelper import GetSharedDataKeys_Helper
    helper = GetSharedDataKeys_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def ClearSharedData ( *args, **kargs ):
    from helpers.datahelper import ClearSharedData_Helper
    helper = ClearSharedData_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetSharedDataScopes ( *args, **kargs ):
    from helpers.datahelper import GetSharedDataScopes_Helper
    helper = GetSharedDataScopes_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def AddSharedDataScope ( *args, **kargs ):
    from helpers.datahelper import AddSharedDataScope_Helper
    helper = AddSharedDataScope_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def ClearSharedDataScopes ( *args, **kargs ):
    from helpers.datahelper import ClearSharedDataScopes_Helper
    helper = ClearSharedDataScopes_Helper()
    helper.configure( *args, **kargs ) 
    return helper.execute( *args, **kargs )

#==============================================================================
def EnableRanging( *args, **kargs ):
    from helpers.rnghelper import EnableRanging_Helper
    helper = EnableRanging_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def DisableRanging ( *args, **kargs ):
    from helpers.rnghelper import DisableRanging_Helper
    helper = DisableRanging_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def SetBasebandConfig ( *args, **kargs ):
    from helpers.rnghelper import SetBasebandConfig_Helper
    helper = SetBasebandConfig_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetBasebandConfig ( *args, **kargs ):
    from helpers.rnghelper import GetBasebandConfig_Helper
    helper = GetBasebandConfig_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def StartRanging ( *args, **kargs ):
    from helpers.rnghelper import StartRanging_Helper
    helper = StartRanging_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetRangingStatus ( *args, **kargs ):
    from helpers.rnghelper import GetRangingStatus_Helper
    helper = GetRangingStatus_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def AbortRanging ( *args, **kargs ):
    from helpers.rnghelper import AbortRanging_Helper
    helper = AbortRanging_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def StartRangingCalibration ( *args, **kargs ):
    from helpers.rnghelper import StartRangingCalibration_Helper
    helper = StartRangingCalibration_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetBasebandNames ( *args, **kargs ):
    from helpers.rnghelper import GetBasebandNames_Helper
    helper = GetBasebandNames_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetAntennaNames ( *args, **kargs ):
    from helpers.rnghelper import GetAntennaNames_Helper
    helper = GetAntennaNames_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GetRangingPaths ( *args, **kargs ):
    from helpers.rnghelper import GetRangingPaths_Helper
    helper = GetRangingPaths_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def GenerateMemoryReport ( *args, **kargs ):
    from helpers.memhelper import GenerateMemoryReport_Helper
    helper = GenerateMemoryReport_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def MemoryLookup( *args, **kargs ):
    from helpers.memhelper import MemoryLookup_Helper
    helper = MemoryLookup_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def CompareMemoryImages( *args, **kargs ):
    from helpers.memhelper import CompareMemoryImages_Helper
    helper = CompareMemoryImages_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

#==============================================================================
def TMTCLookup( *args, **kargs ):
    from helpers.genhelper import TMTCLookup_Helper
    helper = TMTCLookup_Helper()
    helper.configure( *args, **kargs )
    return helper.execute( *args, **kargs )

################################################################################
def RAW_VALUE(item):
    return REGISTRY['TM'][item].raw()

################################################################################
def ENG_VALUE(item):
    return REGISTRY['TM'][item].eng()

################################################################################
class AND(Expression):
    
    def getType(self):
        return AND_TYPE

################################################################################
class OR(Expression):
    
    def getType(self):
        return OR_TYPE


def PCS_GetStatus( *args, **kargs ):
    """
    Get a PCS parameter property.
    
    Syntax 1:
    =========
    
        { Mode: ['MASTER', 'SLAVE', 'ERROR', 'DISCONNECTED'], Version: 'xxx'} = PCS_GetStatus()
        
    Modifiers:
    ==========
        no specific modifiers accepted
        
    Return:
    =======
    
        The PCS Mode and Version.
        
    """
    return True

#==============================================================================
def PCS_IsArqEnabled( *args, **kargs ):
    """
    Check if parameter is Arq Enabled.
    
    Syntax 1:
    =========
    
       True|False = PCS_IsArqEnabled()

    
    Modifiers:
    ==========
    
    Return:
    =======
    
    True if Arq is Enabled
    False in any other case.
    """
    return True

#==============================================================================
def PCS_IsVerifyModeEnabled( *args, **kargs ):
    """
    Check if verify mode is Enabled.
    
    Syntax 1:
    =========

    True|False = PCS_IsVerifyModeEnabled()
    
        
    Modifiers:
    ==========
    No specific modifiers.

    Result:
    =======
    
    True if verify mode is Enabled
    False if not.
    
    """
    return True

 #==============================================================================
def PCS_AbortPtc( *args, **kargs ):
    """
    Abort current PTC request
    
    Syntax 1:
    =========
    
        True|False = PCS_GetStatus()
        
    Modifiers:
    ==========
        no specific modifiers accepted
        
    Return:
    =======
    
        True if function has been executed successfully
        False if there was an issue while executing the function
        
        NOTE: The confirmation of the PTC aborted will be received asynchronous later once the PCS responds
        
    """
    return True

#==============================================================================
def PCS_Send( *args, **kargs ):
    """
    Send a PCS command to the PCS. 
    
    Syntax 1:
    =========
    
    True|False = PCS_Send( command = <tc_item>
                           [, args = <args_list>]
                           [, verify = <tm conditions>]
                           [, <modifier>]... 
                         );
                           
                           <tc_item>
                               e.g. 'P ZPWRMEAS Power measurement'
                               
                               P is the letter to represent that a pseudo command is sent
                               ZPWRMEAS is the pseudo command
                               The remaining part is the description
                               
                           <args_list>
                              The format of the argument list is a list of lists containing:
                                    [ [ <arg name>, <arg value>, {modifiers} ], ... ] 
                            
                                Possible modifiers for each argument are:
                                    
                                    ValueType: LONG,SHORT,STRING,BOOLEAN,TIME,FLOAT     (Default: LONG)
                                    ValueFormat: ENG/RAW/DEF                            (Default: ENG)
                                    Radix: DEC/HEX/OCT                                  (Default: DEC) 
                                    Units: <string>                                     (Default: "")
                                    
                            <modifiers>
                                Modifiers for the command.
                                
                                0. TODO Review: Time:<TIME/datetime string> - Timetag the command with the given time.
                                   No default value.
                                
                                1. Timeout:<float> - Sets the time limit for command execution confirmation. 
                                   Default is 10.0 seconds.
                                                                    
                                2. OnFailure - Determines the list of choices shown to the user in case 
                                   of a failure. It can be a combination ('|')  of the values shown below:: 
                        
                                    - ABORT:       The user may abort the procedure.
                                    - SKIP:        The user may skip this statement and the function returns True
                                    - CANCEL:      The user may skip this statement and the function returns False
                                    - RECHECK:     Repeat the TM verification but not resend the command.
                                    - RESEND:      The command has to be sent again.
                        
                                   Default is ABORT | SKIP | RESEND | CANCEL.        
                        
                                4. Confirm:True/False - Prompt the user for confirmation before sending 
                                   the command. Default is False.
                        
                                5. addInfo:"" - Dictionary of string values used to configure the 
                                   driver at the moment of the command injection. The contents
                                   of this modifier are completely spacecraft-dependent.
                        
                                6. Delay:<seconds> - Time to wait between the command/sequence execution
                                                     confirmation and the TM verifications. Default is 0.
                        
                                7. AdjLimits:True/False - If True and TM conditions are given, the OOL
                                                          definitions of the TM parameters will be adjusted.
    
    Result:
    =======
    
        Note that the PCS will respond:
        //TODO the answer is going to be True / False, not that.
        {success = True|False, stage = 'see accepted values', data = 'xxx' | None, error = 'xxx', None, code = 0}
        
        PCS_Send will respond:
        True: If the PTC was executed successfully or if it is not but the user selected SKIP
        False: In any other case
    

    """
    return True

#==============================================================================
def PCS_Control( *args, **kargs ):
    """
    Same as Send.
    """
    return True

#==============================================================================
def PCS_ReadyToCommand( *args, **kargs ):
    """
    Check if PCS is ready to command
    
    Syntax 1:
    =========
    
       True|False = PCS_ReadyToCommand()

    
    Modifiers:
    ==========
        No specific modifiers required
        
        //TODO Check whether Timeout is required.
    
    Return:
    =======
    
    True if PCS is ready to accept pseudo commands or control commands.
    False in any other case.
    """

    return True
