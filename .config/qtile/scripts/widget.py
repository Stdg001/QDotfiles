import iwlib
import cairocffi
import os
from libqtile import bar, widget
from libqtile.widget import base
from libqtile.log_utils import logger
from qtile_extras.widget.mixins import TooltipMixin, ExtendedPopupMixin
from .popup import *

home = os.path.expanduser('~')
wstyle = "White"

def longNameParse(text): 
    for string in ["Chromium", "Firefox", "Opera", "Visual Studio Code", "Thunar"]: #Add any other apps that have long names here
        if string in text:
            text = string
        else:
            text = text
    return text

class Battery(base._TextBox, TooltipMixin, ExtendedPopupMixin):
    '''Battery life indicator widget.'''
    
    btheme =  'Minimal'
    themepath = home + "/.config/qtile/assets/icons/battery_icon/" + wstyle + '/' + btheme

    filenames = {}

    defaults = [
        ('theme_path', themepath, 'Path of the icons'),
        ('custom_icons', {}, 'dict containing key->filename icon map'),
        ("scaleadd", 0, "Enable/Disable image scaling"),
        ("y_poss", 0, "Modify y possition"),
        ('update_delay', 1, 'The delay in seconds between updates'),

    ]

    def __init__(self, *args, **kwargs):
        base._TextBox.__init__(self, *args, **kwargs)
        TooltipMixin.__init__(self, *args, **kwargs)
        self.add_defaults(TooltipMixin.defaults)
        self.add_defaults(Battery.defaults)
        self.scale = 1.0 / self.scale
        self.lowpopup = True

        self.add_callbacks(
            {
                "Button1": lazy.function(battery_low)
            }
        )
        
        if self.theme_path:
            self.length_type = bar.STATIC
            self.length = 0
        self.surfaces = {}
        self.current_icon = 'battery-missing'
        self.icons = dict([(x, '{0}.png'.format(x)) for x in (
            'battery-missing', 'battery-0', 'battery-0-charge', 'battery-1', 'battery-1-charge', 'battery-2', 'battery-2-charge', 'battery-3', 'battery-3-charge','battery-4', 'battery-4-charge','battery-5', 'battery-5-charge','battery-6', 'battery-6-charge','battery-7', 'battery-7-charge','battery-8', 'battery-8-charge','battery-9', 'battery-9-charge','battery-10', 'battery-10-charge',)])
        self.icons.update(self.custom_icons)

    def timer_setup(self):
        self.update()
        self.timeout_add(self.update_delay, self.timer_setup)

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.setup_images()
    
    def _get_icon_key(self):
        self.binfo = psutil.sensors_battery()

        if self.binfo is None or self.binfo.percent is None:
            key = 'battery-missing'
        else:
            key = f'battery-{int(self.binfo.percent / 10)}'
           
            if self.binfo.power_plugged:
                key += '-charge'
        return key

    def tooltip(self):
        if self.binfo.percent <= 20 and self.lowpopup and not self.binfo.power_plugged:
            self.lowpopup = False
            logger.error(self.lowpopup)
            lazy.function(battery_low)

        if self.binfo.power_plugged:
            self.lowpopup = True
        self.tooltip_text = f"{int(self.binfo.percent)}%"

    def update(self):
        icon = self._get_icon_key()
        self.tooltip()

        if icon != self.current_icon:
            self.current_icon = icon
            self.draw()

    def draw(self):
        if self.theme_path:
            self.drawer.clear(self.background or self.bar.background)
            self.drawer.ctx.set_source(self.surfaces[self.current_icon])
            self.drawer.ctx.paint()
            self.drawer.draw(offsetx=self.offset, width=self.length)
        else:
            self.text = self.current_icon[8:]
            base._TextBox.draw(self)

    def setup_images(self):
        for key, name in self.icons.items():
            path = os.path.join(self.theme_path, name)
            img = cairocffi.ImageSurface.create_from_png(path)
            input_width = img.get_width()
            input_height = img.get_height()

            sp = input_height / (self.bar.height - 1)

            width = input_width / sp
            if width > self.length:
                self.length = int(width) + self.actual_padding * 2

            imgpat = cairocffi.SurfacePattern(img)
            scaler = cairocffi.Matrix()

            scaler.scale(sp, sp)
            scaler.scale(self.scale, self.scale)
            factor = (1 - 1 / self.scale) / 2
            scaler.translate(-width * factor, -width * factor)
            scaler.translate(self.actual_padding * -1, self.y_poss)
            imgpat.set_matrix(scaler)

            imgpat.set_filter(cairocffi.FILTER_BEST)
            self.surfaces[key] = imgpat

class Wifi(Battery):
    '''Wifi Signal Indicator'''

    wtheme =  'Minimal'
    themepath = home + "/.config/qtile/assets/icons/wifi_icon/" + wstyle + '/' + wtheme

    defaults = [
        ('theme_path', themepath, 'Path of the icons'),
        ('custom_icons', {}, 'dict containing key->filename icon map'),
        ("scaleadd", 0, "Enable/Disable image scaling"),
        ("y_poss", 0, "Modify y possition"),
        ('update_delay', 1, 'The delay in seconds between updates'),
        ("interface", "wlan0", "The interface to monitor"),
    ]

    def __init__(self, *args, **kwargs):
        base._TextBox.__init__(self, *args, **kwargs)
        TooltipMixin.__init__(self, *args, **kwargs)
        self.add_defaults(TooltipMixin.defaults)
        # self.add_defaults(Battery.defaults)
        self.add_defaults(Wifi.defaults)

        self.scale = 1.0 / self.scale
        if self.theme_path:
            self.length_type = bar.STATIC
            self.length = 0
        self.surfaces = {}
        self.current_icon = 'wifi-missing'
        self.icons = dict([(x, '{0}.png'.format(x)) for x in (
            'wifi-missing',
            'wifi-bad',
            'wifi-medium',
            'wifi-good',
            'wifi-perfect',
        )])
        self.icons.update(self.custom_icons)

    def get_status(self, interface_name):
        interface = iwlib.get_iwconfig(interface_name)
        if "stats" not in interface:
            return None, None
        quality = interface["stats"]["quality"]
        essid = bytes(interface["ESSID"]).decode()
        return quality, essid
    
    def _get_icon_key(self):
        key = "wifi"
        quality = self.get_status(self.interface)[0]
        if quality is None:
            key += '-missing'
        else:
            if quality <= 17.5:
                key += '-bad'
            elif quality <= 35:
                key += '-medium'
            elif quality <= 52.5:
                key += '-good'
            elif quality <= 70:
                key += '-perfect'
        return key

    def tooltip(self):
        quality, essid = self.get_status(self.interface)
        self.tooltip_text = f'{essid} {quality}'