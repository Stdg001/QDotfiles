import re
import os 
import socket
import subprocess
from typing import List  # noqa: F401
from libqtile import layout, bar, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen, Rule
from libqtile.command import lazy
from libqtile.widget import Spacer
import widgets
mod = "mod4"
mod1 = "alt"
mod2 = "control"
home = os.path.expanduser('~')

keys = [
    # Specials Keys
        Key([mod], "r", lazy.spawn("dmenu_run"), desc="Spawn a command using a prompt widget"),
        Key([mod], "T", lazy.spawn("kitty"), desc="Launch terminal"),
        Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    # Window buttons
        # Change focus
            Key([mod], "left", lazy.layout.left(), desc="Move focus to left"),
            Key([mod], "right", lazy.layout.right(), desc="Move focus to right"),
            Key([mod], "down", lazy.layout.down(), desc="Move focus down"),
            Key([mod], "up", lazy.layout.up(), desc="Move focus up"),
            Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),

        # Move windows on the layout
            Key([mod, "shift"], "left", lazy.layout.shuffle_left(), desc="Move window to the left"),
            Key([mod, "shift"], "right", lazy.layout.shuffle_right(), desc="Move window to the right"),
            Key([mod, "shift"], "down", lazy.layout.shuffle_down(), desc="Move window down"),
            Key([mod, "shift"], "up", lazy.layout.shuffle_up(), desc="Move window up"),
  
        # Change window size
            Key([mod, "control"], "left", lazy.layout.grow_left(), desc="Grow window to the left"),
            Key([mod, "control"], "right", lazy.layout.grow_right(), desc="Grow window to the right"),
            Key([mod, "control"], "down", lazy.layout.grow_down(), desc="Grow window down"),
            Key([mod, "control"], "up", lazy.layout.grow_up(), desc="Grow window up"),
            Key([mod, "control"], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    
    # Layout buttons
        Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    
    # System buttons
        Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
        Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
]


groups = []

group_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",]

group_labels = ["", "", "", "", "", "", "", "", "", "",]

group_layouts = ["max", "matrix", "matrix", "matrix", "matrix", "matrix", "matrix", "matrix", "matrix", "matrix",]

for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            layout=group_layouts[i].lower(),
            label=group_labels[i],
        ))

def init_layout_theme():
    return {"margin":5,
            "border_width":2,
            "border_focus": "#5e81ac",
            "border_normal": "#4c566a"
            }

layout_theme = init_layout_theme()

layouts = [
    #layout.MonadTall(margin=8, border_width=2, border_focus="#5e81ac", border_normal="#4c566a"),
    # layout.MonadTall(**layout_theme),
    # #layout.MonadWide(margin=8, border_width=2, border_focus="#5e81ac", border_normal="#4c566a"),
    # layout.MonadWide(**layout_theme),
    layout.Matrix(**layout_theme),
    # layout.Bsp(**layout_theme),
    # layout.Floating(**layout_theme),
    # layout.RatioTile(**layout_theme),
    layout.Max(**layout_theme)
]

def init_colors():
    return [["#2F343F", "#2F343F"], # color 0
            ["#2F343F", "#2F343F"], # color 1
            ["#c0c5ce", "#c0c5ce"], # color 2
            ["#fba922", "#fba922"], # color 3
            ["#3384d0", "#3384d0"], # color 4
            ["#f3f4f5", "#f3f4f5"], # color 5
            ["#cd1f3f", "#cd1f3f"], # color 6
            ["#62FF00", "#62FF00"], # color 7
            ["#6790eb", "#6790eb"], # color 8
            ["#a9a9a9", "#a9a9a9"]] # color 9

colors = init_colors()

def init_widgets_defaults():
    return dict(font="Noto Sans",
                fontsize = 12,
                padding = 2,
                background=colors[1])

widget_defaults = init_widgets_defaults()

def init_widgets_list():
    widgets_list = [
                widget.GroupBox(
                    font="FontAwesome",
                    fontsize = 16,
                    margin_y = -1,
                    margin_x = 0,
                    padding_y = 6,
                    padding_x = 5,
                    borderwidth = 0,
                    disable_drag = True,
                    active = colors[9],
                    inactive = colors[5],
                    rounded = False,
                    highlight_method = "text",
                    this_current_screen_border = colors[8],
                    foreground = colors[2],
                    background = colors[1]
               ),
                widget.Sep(
                    linewidth = 1,
                    padding = 10,
                    foreground = colors[2],
                    background = colors[1]
                ),
                widget.CurrentLayout(
                    font = "Noto Sans Bold",
                    foreground = colors[5],
                    background = colors[1]
                ),
               widget.Sep(
                    linewidth = 1,
                    padding = 10,
                    foreground = colors[2],
                    background = colors[1]
                ),
               widget.TaskList(
                    font="Noto Sans",
                    fontsize = 12,
                    foreground = colors[5],
                    background = colors[1],
                    theme_mode="fallback",
                    txt_floating="",
                    txt_maximized="",
                    txt_minimized="",
                    highlight_method="block",

                ),
               # widget.Net(
               #          font="Noto Sans",
               #          fontsize=12,
               #          interface="enp0s31f6",
               #          foreground=colors[2],
               #          background=colors[1],
               #          padding = 0,
               #          ),
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               # widget.NetGraph(
               #          font="Noto Sans",
               #          fontsize=12,
               #          bandwidth="down",
               #          interface="auto",
               #          fill_color = colors[8],
               #          foreground=colors[2],
               #          background=colors[1],
               #          graph_color = colors[8],
               #          border_color = colors[2],
               #          padding = 0,
               #          border_width = 1,
               #          line_width = 1,
               #          ),
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               # # do not activate in Virtualbox - will break qtile
               # widget.ThermalSensor(
               #          foreground = colors[5],
               #          foreground_alert = colors[6],
               #          background = colors[1],
               #          metric = True,
               #          padding = 3,
               #          threshold = 80
               #          ),
               # # battery option 1  ArcoLinux Horizontal icons do not forget to import arcobattery at the top
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               # arcobattery.BatteryIcon(
               #          padding=0,
               #          scale=0.7,
               #          y_poss=2,
               #          theme_path=home + "/.config/qtile/icons/battery_icons_horiz",
               #          update_interval = 5,
               #          background = colors[1]
               #          ),
               # # battery option 2  from Qtile
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               # widget.Battery(
               #          font="Noto Sans",
               #          update_interval = 10,
               #          fontsize = 12,
               #          foreground = colors[5],
               #          background = colors[1],
	           #          ),
               # widget.TextBox(
               #          font="FontAwesome",
               #          text="  ",
               #          foreground=colors[6],
               #          background=colors[1],
               #          padding = 0,
               #          fontsize=16
               #          ),
               # widget.CPUGraph(
               #          border_color = colors[2],
               #          fill_color = colors[8],
               #          graph_color = colors[8],
               #          background=colors[1],
               #          border_width = 1,
               #          line_width = 1,
               #          core = "all",
               #          type = "box"
               #          ),
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               # widget.TextBox(
               #          font="FontAwesome",
               #          text="  ",
               #          foreground=colors[4],
               #          background=colors[1],
               #          padding = 0,
               #          fontsize=16
               #          ),
               # widget.Memory(
               #          font="Noto Sans",
               #          format = '{MemUsed}M/{MemTotal}M',
               #          update_interval = 1,
               #          fontsize = 12,
               #          foreground = colors[5],
               #          background = colors[1],
               #         ),
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               widget.TextBox(
                    font="FontAwesome",
                    text="  ",
                    foreground=colors[3],
                    background=colors[1],
                    padding = 0,
                    fontsize=16
                ),
               widget.Clock(
                    foreground = colors[5],
                    background = colors[1],
                    fontsize = 12,
                    format="%Y-%m-%d %H:%M"
                ),
               # widget.Sep(
               #          linewidth = 1,
               #          padding = 10,
               #          foreground = colors[2],
               #          background = colors[1]
               #          ),
               widget.Systray(
                    background=colors[1],
                    icon_size=20,
                    padding = 10
                ),
                widgets.WifiIcon(
                    padding=-2,
                    scale=0.9,
                    y_poss=0.3,
                    update_interval = 5,
                    update_delay= 1,
                    interface='wlo1'
                ),
                widgets.BatteryIcon(
                    padding=3,
                    scale=0.7,
                    y_poss=-1.3,
                    update_interval = 5,
                    update_delay= 0.2
                        ),
                widget.Battery(
                    font="NotoSans",
                    format='{percent:2.0%}',
                    update_interval = 5,
                    update_delay= 0.2
                ),
                widget.Spacer(
                    length= 2
                ),
              ]
    return widgets_list

widgets_list = init_widgets_list()

def init_widgets_screen1():
    widgets_screen1 = init_widgets_list()
    return widgets_screen1

def init_widgets_screen2():
    widgets_screen2 = init_widgets_list()
    return widgets_screen2

def init_screens():
    return [
        Screen(
            top=bar.Bar(
                widgets=init_widgets_screen1(),
                size=26,
                opacity=0.8,),
            wallpaper=home + "/.config/qtile/wallpapers/arch-chan.png",
            wallpaper_mode= "stretch"
        )
    ]
screens = init_screens()

@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/scripts/autostart.sh'])

@hook.subscribe.startup
def start_always():
    subprocess.Popen(['xsetroot', '-cursor_name', 'left_ptr'])

floating_types = ["notification", "toolbar", "splash", "dialog"]
