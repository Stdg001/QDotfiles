import subprocess
from libqtile import hook, layout
from libqtile.config import Match, Key, Group, Screen, Drag, Click
from libqtile.utils import guess_terminal
from qtile_extras import widget as widgetx
from scripts.widget import *
import test

battery_info = psutil.sensors_battery()

@hook.subscribe.startup_complete
def autostart():
    subprocess.call([f'{home}/.config/qtile/scripts/autostart.sh'])

# █▄▀ █▀▀ █▄█ █▄▄ █ █▄ █ █▀▄ █▀
# █ █ ██▄  █  █▄█ █ █ ▀█ █▄▀ ▄█

mod = "mod4"
keys = [

    #################
    #  BASIC MOVES  #
    #################

    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),

    Key([mod, "control"], "Up",
        lazy.layout.grow_up(),
        lazy.layout.grow()
        ),

    Key([mod, "control"], "Down",
        lazy.layout.grow_down(),
        lazy.layout.shrink()),

    Key([mod, "control"], "Left", lazy.layout.grow_left()),
    Key([mod, "control"], "Right", lazy.layout.grow_right()),

    Key([mod, "shift"], "Left", lazy.layout.shuffle_left()),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right()),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up()),

    Key([mod], "bar", lazy.spawn("python .config/qtile/scripts/toggle_between_screens.py")),
    Key([mod], "p", lazy.layout.flip()),
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod], "w", lazy.window.kill()),
    Key([mod, "control"], "r", lazy.restart()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "space", lazy.window.toggle_floating()),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "b", lazy.hide_show_bar("all")),

    ################
    #     APPS     #
    ################

    Key([mod], "m", lazy.spawn("rofi -show drun")),
    Key([mod], "e", lazy.spawn("thunar")),
    Key([mod], "t", lazy.spawn(guess_terminal())),

    ################
    # SPECIAL KEYS #
    ################

    Key([], "XF86AudioLowerVolume", lazy.spawn("pamixer --decrease 5"), lazy.function(Volume.show_popup)),
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pamixer --increase 5"), lazy.function(Volume.show_popup)),
    Key([], "XF86AudioMute", lazy.spawn("pamixer --toggle-mute"), lazy.function(Volume.show_popup)),

    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous")),
    Key([], "XF86AudioStop", lazy.spawn("playerctl stop")),

    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +10%")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 10%-")),

    ################
    #    POP UPS   #
    ################

    Key([mod], "F3", lazy.function(screen_menu))
]

mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position()),
    Drag(
        [mod],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.toggle_floating())
]

# █▄▄ ▄▀█ █▀█
# █▄█ █▀█ █▀▄

screens = [
    Screen(
        bottom=bar.Bar([
            widget.TextBox(
                text="",
                fontsize=35,
                foreground='#0000004D',
                padding=0),

            widget.TaskList(
                font="Cascadia Code",
                rounded = True,
                theme_mode="fallback",
                foreground=colors["text"],
                background='#0000004D',
                txt_floating="",
                txt_maximized="",
                txt_minimized="",
                highlight_method="block",
                parse_text = longNameParse),

            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["surface1"],
                background='#0000004D',
                padding=0),

            widgetx.StatusNotifier(
                padding=10,
                icon_size=25,
                background=colors["surface1"]),
            
            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["surface2"],
                background=colors["surface1"],
                padding=0),

            Battery(
                scale=0.7,
                y_poss=-2,
                update_delay= 1,
                popup_layout = Battery.popup,
                popup_hide_timeout = 0,
                popup_show_args = {"relative_to": 5, "relative_to_bar": True},
                background = colors["surface2"]),

            Volume(
                background=colors["surface2"],
                scale=0.8,
                y_poss=-1,
                update_delay= 1,
                padding=-3),

            Wifi(
                background=colors["surface2"],
                padding = -4,
                scale=0.6,
                y_poss=1,
                update_delay= 1,
                interface='wlan0'),

            widget.TextBox(
                text="",
                fontsize=35,
                foreground=colors["mantle"],
                background=colors["surface2"],
                padding=0),

            widget.Clock(
                background=colors["mantle"],
                foreground=colors["text"],
                format="%H:%M\n%d/%m/%Y",
                font="Cascadia Code",
                fontsize=12.5,
                padding=0),

            widget.TextBox(
                text="",
                fontsize=30,
                foreground=colors["mantle"],
                padding=0)],
            size=30, 
            background='#00000000',
            margin=[0,5,5,5]
        )
    )
]

# █  ▄▀█ █▄█ █▀█ █ █ ▀█▀
# █▄ █▀█  █  █▄█ █▄█  █

layout_conf = {
        "border_normal": colors["base"],
        "border_focus": colors["lavender"],
        "border_width": 4,
        "margin": 10}

layout_conf_bsp = {
    "border_normal": colors["base"],
    "border_focus": colors["lavender"],
    "border_on_single": True,
    "border_width": 3,
    "margin": 5,
    "grow_amount": 5,
    "fair": False,
    "ratio": 1.3}

layout_conf_max = {
    "border_normal": colors["base"],
    "border_focus": colors["lavender"],
    "border_width": 0,
    "margin": 5}

layouts = [
    layout.Max(**layout_conf_max),
    layout.Bsp(**layout_conf_bsp)]

floating_layout = layout.Floating(float_rules=[
    *layout.Floating.default_float_rules,
    Match(title='branchdialog'),
    Match(title='pinentry'),
    Match(wm_class='confirmreset'),
    Match(wm_class='makebranch'),
    Match(wm_class='maketag'),
    Match(wm_class='ssh-askpass'),
    Match(wm_class='pavucontrol'),
    Match(wm_class='nitrogen'),
    Match(wm_class='lxappearance'),
    Match(wm_class='android-studio'),
    Match(wm_class='python2.7'),
    Match(wm_class='launcher-4'),
    Match(wm_class='stacer'),
    Match(wm_class='VirtualBox Manager'),
    Match(wm_class='VirtualBox Machine')
], **layout_conf)

# █▀▀ █▀█ █▀█ █ █ █▀█ █▀
# █▄█ █▀▄ █▄█ █▄█ █▀▀ ▄█

groups = [
    Group("1", label=""),
    Group("2", label=""),
    Group("3", label="")]

for i, group in enumerate(groups):
    actual_key = str(i + 1)
    keys.extend([
        # Switch to workspace N
        Key([mod], actual_key, lazy.group[group.name].toscreen(toggle=True)),
        # Send window to workspace N
        Key([mod, "shift"], actual_key, lazy.window.togroup(group.name))])