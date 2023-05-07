from libqtile import bar, widget
from libqtile.config import Screen
from qtile_extras import widget as widgetx
from libqtile.lazy import lazy
from .catppuccin import colors
from .widget import *
import os

home = os.path.expanduser('~')
colors = colors["frappe"]

def longNameParse(text): 
    for string in ["Chromium", "Firefox", "Opera", "Visual Studio Code", "Thunar"]: #Add any other apps that have long names here
        if string in text:
            text = string
        else:
            text = text
    return text

screens = [
    Screen(
        bottom=bar.Bar(
        [
            # Left side

            widget.TextBox(
                text="",
                fontsize=35,
                foreground='#0000004D',
                padding=0),

            widget.TaskList(
                font="Cascadia Code",
                icon_size = 19,
                rounded = True,
                theme_mode="fallback",
                foreground=colors["text"],
                background='#0000004D',
                opacity= .5,
                txt_floating="",
                txt_maximized="",
                txt_minimized="",
                highlight_method="block",
                parse_text = longNameParse),

            # Right side
            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["surface2"],
                background='#0000004D',
                padding=0),

            BatteryIcon(
                    background=colors["surface2"],
                    padding=3,
                    scale=0.7,
                    y_poss=-1.3,
                    update_delay= 1),
            
            WifiIcon(
                    background=colors["surface2"],
                    padding=-2,
                    scale=0.8,
                    y_poss=1,
                    update_delay= 1,
                    interface='wlo1'
                ),
            widget.PulseVolume(
                background=colors["surface2"],
                foreground=colors["text"],
                font="Cascadia Code",
                fontsize=20,
                fmt="󰕾 {} ",
                mouse_callbacks={
                    'Button3': lazy.spawn('pavucontrol -t 4')}),
            
            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["surface2"],
                padding=0),
        
        ], 
        size=30,
        background='#00000000',
        margin=[0,10,5,10]),

        top=bar.Bar([
            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["mantle"],
                padding=0),

            widget.Clock(
                background=colors["mantle"],
                foreground=colors["text"],
                format=" %d/%m/%Y  %H:%M ",
                font="Cascadia Code",
                fontsize=20,
                padding=0),

            widget.TextBox(
                text="",
                fontsize=30,
                foreground=colors["mantle"],
                background=colors["surface1"],
                padding=0),

            widgetx.StatusNotifier(
                padding=10,
                icon_size=25,
                background=colors["surface1"]),

            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["surface1"],
                padding=0),
            
            widget.Spacer(length=833),

            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["lavender"],
                padding=0),

            widget.GroupBox(
                background=colors["lavender"],
                other_screen_border=colors["lavender"],
                other_current_screen_border=colors["lavender"],
                this_screen_border=colors["lavender"],
                this_current_screen_border=colors["lavender"],
                active=colors["overlay1"],
                inactive=colors["text"],
                block_highlight_text_color=colors["mantle"],
                fontsize=15,
                padding_x=15,
                use_mouse_wheel=False,
                font='Roboto Mono',
                disable_drag=True),

            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["lavender"],
                padding=0),
        ],
        size=30, 
        background='#00000000',
        margin=[5,10,0,10]),
    )
]
