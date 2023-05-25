from qtile_extras.popup.toolkit import * 
from libqtile.lazy import lazy
from .catppuccin import *
import psutil
import alsaaudio

colors = colors[style]

def screen_menu(qtile):
    controls = [
        PopupImage(
            filename="/home/Stvll/.config/qtile/assets/sources/laptop.png",
            pos_x=0,
            pos_y=-0.05,
            width=0.25,
            height=0.25,
            can_focus=False,
            background="#00000000",
            mouse_callbacks={
                "Button1": lazy.spawn('notify-send -u normal -t 0 "test" "m1"')}),

        PopupImage(
            filename="/home/Stvll/.config/qtile/assets/sources/monitor.png",
            pos_x=0.25,
            pos_y=-0.03,
            width=0.15,
            height=0.15,
            can_focus=False,
            mask=True,
            colour="#808080",
            background="#00000000",
            mouse_callbacks={
                "Button1": lazy.spawn('notify-send -u normal -t 0 "test" "m2"')}),

        PopupText(
            text="hola",
            font='Cascadia Code',
            background="#00000000",
            pos_x=0.5,
            pos_y=-0.03,
            width=0.15,
            height=0.15,
        )
    ]

    layout = PopupRelativeLayout(
        qtile,
        width=300, 
        height= 500,
        hide_on_timeout=5,
        controls=controls,
        background=colors['baset'],
        close_on_click = False,)

    layout.show(
        x= -10,
        relative_to= 6)

def battery_low(qtile):
    battery_status = psutil.sensors_battery()

    controls = [
        PopupCircularProgress(
            pos_x=0.2,
            pos_y=0.2,
            width=0.6,
            height=0.6,
            max_value = 100,
            value=int(battery_status.percent)),

        PopupText(
            text= str(int(battery_status.percent)),
            font='Cascadia Code',
            background="#00000000",
            pos_x=0.5,
            pos_y=-0.03,
            width=0.15,
            height=0.15)

    ]

    layout = PopupRelativeLayout(
        qtile,
        width=200, 
        height= 200,
        controls=controls,
        background=colors['baset'],
        close_on_click = True)

    layout.show(
        x= -10,
        relative_to= 5)

def volume(qtile):
    Mixer = alsaaudio.Mixer(control='Master', id=0, cardindex=-1, device='default')    
    volume = Mixer.getvolume()[0]
    
    if Mixer.getmute()[0] == 1:
        volume = 0

    if volume > 0: img = 'sound'
    elif volume == 0:
        img = 'nosound'

    controls = [
        PopupImage(
            filename=f"/home/Stvll/.config/qtile/assets/sources/{img}.png",
            pos_x=-0.4,
            pos_y=-0,
            width=1,
            height=1,
            background="#00000000"),
        
        PopupSlider(
            pos_x=0.2,
            background="#00000000",
            pos_y=0.2,
            width=0.8,
            height=0.6,
            value=volume,
            max_value=100,
        )
    ]
    layout = PopupRelativeLayout(
        qtile,
        width=200,
        height=35,
        hide_on_timeout=1,
        controls=controls,
        background=colors['baset'],)
    
    layout.show(
        y = -5,
        x = -10,
        relative_to = 9, 
        relative_to_bar = True)