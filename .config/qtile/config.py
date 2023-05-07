import os
import subprocess
from libqtile import hook, qtile

from settings.groups import groups
from settings.mouse import mouse
from settings.screens import screens
from settings.keys import keys, mod
from settings.layouts import layouts, layout_conf, floating_layout

home = os.path.expanduser('~/.config/qtile/autostart.sh')

@hook.subscribe.startup_complete
def autostart():
    subprocess.call([home])