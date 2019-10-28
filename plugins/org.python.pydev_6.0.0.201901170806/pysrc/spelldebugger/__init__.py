from spell.lang.functions import *
from spell.lang.constants import *
from spell.lang.modifiers import *
try:
    import spellwrapper
except:
    pass
try:
    import spelldebugger.spellwrapper
except:
    pass
try:
    import spelldebugger.spellwrapper as spellwrapper
except:
    pass
#__all__ = ['spellwrapper']