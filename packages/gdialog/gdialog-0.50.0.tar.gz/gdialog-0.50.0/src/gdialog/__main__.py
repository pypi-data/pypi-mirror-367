#!/home/twinkle/venv/bin/python

import argparse

######################################################################
# LIBS

import gdialog
from gdialog import run

import gdialog.dialog
from gdialog.dialog import *

######################################################################
# DEFS

def main(args):

    msgs = args.m if args.m is not None else "Nothing To Do."
    labl = args.l if args.l is not None else "Sample Dialog"
    titl = args.t if args.t is not None else "gdialog"
    icon = None
    btns = None
    mkup = args.M
    txvw = args.T

    i = args.i.lower() if args.i is not None else 'o'

    if i == 'w' or i == 'warn':
        icon = GTK_MESSAGE_WARNING
    elif i == 'q' or i == 'que' or i == 'question':
        icon = GTK_MESSAGE_QUESTION
    elif i == 'e' or i == 'err' or i == 'error':
        icon = GTK_MESSAGE_ERROR
    else:
        icon = GTK_MESSAGE_INFO

    b = args.b.lower() if args.b is not None else 'ok'

    if b == 'cl' or b == 'clo' or b == 'close':
        btns = GTK_BUTTONS_CLOSE
    elif b == 'ca' or b == 'can' or b == 'cancel':
        btns = GTK_BUTTONS_CANCEL
    elif b == 'yn' or b == 'yesno':
        btns = GTK_BUTTONS_YES_NO
    elif b == 'oc' or b == 'okcan' or i == 'ok&cancel':
        btns = GTK_BUTTONS_OK_CANCEL
    else:
        btns = GTK_BUTTONS_OK

    run(msgs, labl, titl, icon, btns, txvw, mkup)

######################################################################
# MAIN
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str, help='message', required=False)
    parser.add_argument('-l', type=str, help='label', required=False)
    parser.add_argument('-t', type=str, help='title', required=False)
    parser.add_argument('-i', type=str, help='icon [o:ok|w:warn|e:err(or)|q:que(stion)]', required=False)
    parser.add_argument('-b', type=str, help='button [ok|cl(ose)|can(cel)|yn(yesno)|oc(ok&cancel)]', required=False)
    parser.add_argument('--M', action="store_true", help='Use Markup (for Only Message Dialog)', required=False)
    parser.add_argument('--T', action="store_true", help='Use TextView (Disable Icon and Buttons)', required=False)
    main(parser.parse_args())

""" __DATA__

__END__ """
