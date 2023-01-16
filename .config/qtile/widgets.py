from __future__ import division

import iwlib
import cairocffi
import os
from libqtile import bar, images
from libqtile.widget import base
from libqtile.log_utils import logger
from pathlib import Path
import cv2
import numpy as np

home = os.path.expanduser('~')
thememode = "Minimal_white"

class BatteryIcon(base._TextBox):
    """Battery life indicator widget."""
    
    themepath = home + "/.config/qtile/icons/battery_icon/" + thememode
    
    BATTERY_INFO_FILES = {
    'energy_now_file': ['energy_now', 'charge_now'],
    'energy_full_file': ['energy_full', 'charge_full'],
    'power_now_file': ['power_now', 'current_now'],
    'status_file': ['status'],}

    filenames = {}

    defaults = [
        ('fontshadow', None, 'Set shadow to the font'),
        ('font', 'Sans', 'Font to battery indicator'),
        ('fontsize', 12, 'Font size'),
        ('theme_path', themepath, 'Path of the icons'),
        ('custom_icons', {}, 'dict containing key->filename icon map'),
        ("scaleadd", 0, "Enable/Disable image scaling"),
        ("y_poss", 0, "Modify y possition"),
        ('battery_name', 'BAT0', 'ACPI name of a battery, usually BAT0'),
        ('status_file', 'status', 'Name of status file in /sys/class/power_supply/battery_name'),
        ('energy_now_file', None, 'Name of file with the current energy in /sys/class/power_supply/battery_name'),
        ('energy_full_file', None, 'Name of file with the maximum energy in /sys/class/power_supply/battery_name'),
        ('power_now_file', None, 'Name of file with the current power draw in /sys/class/power_supply/battery_name'),
        ('update_delay', 1, 'The delay in seconds between updates'),
    ]

    def __init__(self, **config):
        base._TextBox.__init__(self, "BAT", bar.CALCULATED, **config)
        self.add_defaults(BatteryIcon.defaults)
        self.scale = 1.0 / self.scale

        if self.theme_path:
            self.length_type = bar.STATIC
            self.length = 0
        self.surfaces = {}
        self.current_icon = 'battery-missing'
        self.icons = dict([(x, '{0}.png'.format(x)) for x in (
            'battery-missing',
            'battery-0', 'battery-0-charge',
            'battery-10', 'battery-10-charge',
            'battery-20', 'battery-20-charge',
            'battery-30', 'battery-30-charge',
            'battery-40', 'battery-40-charge',
            'battery-50', 'battery-50-charge',
            'battery-60', 'battery-60-charge',
            'battery-70', 'battery-70-charge',
            'battery-80', 'battery-80-charge',
            'battery-90', 'battery-90-charge',
            'battery-full', 'battery-full-charge',
            # 'battery-full-charged',
        )])
        self.icons.update(self.custom_icons)

    def _load_file(self, name):
        try:
            path = os.path.join('/sys/class/power_supply', self.battery_name, name)
            with open(path, 'r') as f:
                return f.read().strip()
        except IOError:
            if name == 'current_now':
                return 0
            return False

    def _get_param(self, name):
        if name in self.filenames and self.filenames[name]:
            return self._load_file(self.filenames[name])
        elif name not in self.filenames:
            file_list = self.BATTERY_INFO_FILES.get(name, [])[:]
            if getattr(self, name, None):
                file_list.insert(0, getattr(self, name))
            for file in file_list:
                value = self._load_file(file)
                if value is not False and value is not None:
                    self.filenames[name] = file
                    return value

        self.filenames[name] = None
        return None

    def _get_info(self):
        try:
            info = {
                'stat': self._get_param('status_file'),
                'now': float(self._get_param('energy_now_file')),
                'full': float(self._get_param('energy_full_file')),
                'power': float(self._get_param('power_now_file')),
            }
        except TypeError:
            return False
        return info

    def timer_setup(self):
        self.update()
        self.timeout_add(self.update_delay, self.timer_setup)

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.setup_images()
        self.setup_text()

    def _get_icon_key(self):
        key = 'battery'
        info = self._get_info()
        if info is False or not info.get('full'):
            key += '-missing'
        else:
            percent = info['now'] / info['full']
            if percent < .1:
                key += '-0'
            elif percent < .2:
                key += '-10'
            elif percent < .3:
                key += '-20'
            elif percent < .4:
                key += '-30'
            elif percent < .5:
                key += '-40'
            elif percent < .6:
                key += '-50'
            elif percent < .5:
                key += '-60'
            elif percent < .8:
                key += '-70'
            elif percent < .9:
                key += '-80'
            elif percent < 1:
                key += '-90'
            else:
                key += '-full'

            if info['stat'] == 'Charging':
                key += '-charge'
            elif info['stat'] == 'Full':
                key += '-charged'
        return key

    def update(self):
        icon = self._get_icon_key()
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

    def setup_text(self):
        info = self._get_info()
        percent = info['now'] / info['full']
        self.textlayout = self.drawer.textlayout("", "ffffff", self.font, self.fontsize, self.fontshadow, wrap=False)

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

class WifiIcon(base.InLoopPollText):
    
    home = os.path.expanduser('~')
    thememode = "Minimal_white"
    themepath = home + "/.config/qtile/icons/wifi_icon/" + thememode + ".png"

    defaults = [
        ('theme_path', themepath, 'Path of the icons'),
        ('custom_icons', {}, 'dict containing key->filename icon map'),
        ("scaleadd", 0, "Enable/Disable image scaling"),
        ("y_poss", 0, "Modify y possition"),
        ("interface", "wlan0", "The interface to monitor"),
        ("update_interval", 1, "The update interval."),
    ]

    def __init__(self, **kwargs):
        super().__init__(update_interval=self.update_interval, **kwargs)

    def get_status(self, interface_name):
        interface = iwlib.get_iwconfig(interface_name)
        if "stats" not in interface:
            return None, None
        quality = interface["stats"]["quality"]
        essid = bytes(interface["ESSID"]).decode()
        return quality

    def get_img(self):
        imagen = cv2.imread(self.themepath)
        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGBA)
        result = np.zeros(imagen.shape,dtype=np.uint8)
        gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        quality = self.get_status(self.interface)
        mask = np.zeros(imagen.shape, dtype=np.uint8)

        for i, contorno in enumerate(contornos):
            if quality < (17.5 * (i + 1)):
                cv2.drawContours(mask, [contorno], -1, (255, 255, 255, 0.7*255), -1)
            else:
                cv2.drawContours(mask, [contorno], -1, (255, 255, 255, 1*255), -1)

        result = cv2.bitwise_and(imagen, mask)
        return result

    def text(self):
        quality = get_status(self.interface)
        return str(quality)

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        self.drawer.ctx.draw_image(self.get_img(), 0, 0)