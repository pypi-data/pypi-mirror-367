#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

import gdialog.dialog
from gdialog.dialog import *

######################################################################
# VARS

MessageType = {
     'GTK_MESSAGE_INFO': 0,
  'GTK_MESSAGE_WARNING': 1,
 'GTK_MESSAGE_QUESTION': 2,
    'GTK_MESSAGE_ERROR': 3,
    'GTK_MESSAGE_OTHER': 4,
}

ButtonType = {
      'GTK_BUTTONS_NONE': 0,
        'GTK_BUTTONS_OK': 1,
     'GTK_BUTTONS_CLOSE': 2,
    'GTK_BUTTONS_CANCEL': 3,
    'GTK_BUTTONS_YES_NO': 4,
 'GTK_BUTTONS_OK_CANCEL': 5,
}

ResponseType = {
         'GTK_RESPONSE_NONE': -1,
       'GTK_RESPONSE_REJECT': -2,
       'GTK_RESPONSE_ACCEPT': -3,
 'GTK_RESPONSE_DELETE_EVENT': -4,
           'GTK_RESPONSE_OK': -5,
       'GTK_RESPONSE_CANCEL': -6,
        'GTK_RESPONSE_CLOSE': -7,
          'GTK_RESPONSE_YES': -8,
           'GTK_RESPONSE_NO': -9,
        'GTK_RESPONSE_APPLY': -10,
         'GTK_RESPONSE_HELP': -11,
}

######################################################################
# DEFS

def run(m:str="Nothing To Do.", l:str="Sample Dialog", t:str="gdialog", i:int=GTK_MESSAGE_INFO, b:int=GTK_BUTTONS_OK, txvw:bool=False, mkup:bool=False):
    if txvw is True:
        return gtxview(m, l, t, i, b, mkup)
    else:
        return gdialog(m, l, t, i, b, mkup)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["run", "MessageType", "ButtonType", "ResponseType"]

""" __DATA__

__END__ """
