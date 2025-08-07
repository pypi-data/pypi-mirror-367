# gdialog

Simple GTK Dialog.

-----
## Usage

1. Library Module

```python

from gdialog.dialog import * # Include GTK Values(MessageType, ButtonType, ResponseType)
from gdialog import run

run("This is Message, Nothing To Do.", "Sample Dialog Label", "Sample Title", GTK_MESSAGE_INFO, GTK_BUTTONS_OK, txvw=False, mkup=False):

```

2. Commandline

```markdown
python -m gdialog -m 'dialog message test' -l 'dialog label' -t 'dialog title' -i ok -b ok

usage: [-h] [-m M] [-l L] [-t T] [-i I] [-b B] [--M] [--T]

options:
  -h, --help  show this help message and exit
  -m M        message
  -l L        label
  -t T        title
  -i I        icon [o:ok|w:warn|e:err(or)|q:que(stion)]
  -b B        button [ok|cl(ose)|can(cel)|yn(yesno)|oc(ok&cancel)]
  --M         Use Markup (for Only Message Dialog)
  --T         Use TextView (Disable Icon and Buttons)
```
-----
## Requirement

 * least needs gtk version 2.40
 * gtk2.0 dev package (libgtk+-2.0) or later (gtk+-3.0)
 * unsupported gtk+-4.0

