import alsaaudio
import psutil
import iwlib
from PIL import Image
import cairocffi
from libqtile.log_utils import logger
from libqtile import bar, widget
from libqtile.widget import base
from libqtile.lazy import lazy
from qtile_extras.widget.mixins import TooltipMixin, ExtendedPopupMixin
from qtile_extras.popup.toolkit import *
import netifaces
import glob
import os

home = os.path.expanduser('~')
wlan = netifaces.gateways()['default'][netifaces.AF_INET][1]

color = "White"
wstyle = 'Minimal'

def longNameParse(text):
    long_names = ["Chromium", 'GIMP', "Firefox", "Opera", "Visual Studio Code", "Thunar"]
    return next((name for name in long_names if name in text), text)

class DefWidget(base._TextBox, TooltipMixin, ExtendedPopupMixin):
    defaults = [
        ("y_poss", 0, "Modify y position"),
        ("scale", 1, "Icons size"),
        ('update_delay', 1, 'The delay in seconds between updates'),
    ]

    def __init__(self, *args, **kwargs):
        base._TextBox.__init__(self, *args, **kwargs)
        TooltipMixin.__init__(self, *args, **kwargs)
        ExtendedPopupMixin.__init__(self, **kwargs)
        self.add_defaults(ExtendedPopupMixin.defaults)
        self.add_defaults(TooltipMixin.defaults)
        self.add_defaults(self.defaults)

        self.scale = 1.0 / self.scale
        self.length_type = bar.STATIC
        self.icon_width = 0

        self.current_icons = ()
        self.surfaces = {}

    def png(self, carpeta):
        return [
            (os.path.dirname(path), os.path.splitext(os.path.basename(path))[0])
            for path in glob.glob(os.path.join(carpeta, "*.png"))
        ]

    def setup_images(self):
        for path, key in self.imgs:
            img_path = os.path.join(path, f'{key}.png')
            with Image.open(img_path) as img:
                input_width, input_height = img.size
            sp = input_height / (self.bar.height - 1)
            width = input_width / sp
            img = cairocffi.ImageSurface.create_from_png(img_path)
            imgpat = cairocffi.SurfacePattern(img)
            scaler = cairocffi.Matrix()
            scaler.scale(sp, sp)
            scaler.scale(self.scale, self.scale)
            factor = (1 - 1 / self.scale) / 2
            scaler.translate(-width * factor, -width * factor)
            scaler.translate(self.padding -1, self.y_poss)
            imgpat.set_matrix(scaler)
            imgpat.set_filter(cairocffi.FILTER_BEST)
            self.surfaces[key] = imgpat, int(width)

    def draw(self):
        offset = self.offset
        self.length = 0
        for key in self.current_icons:
            if key is None or key not in self.surfaces:
                continue
            self.drawer.clear(self.background or self.bar.background)
            surface, width = self.surfaces[key]
            self.length += width

            self.drawer.ctx.set_source(surface)
            self.drawer.ctx.paint()
            self.drawer.draw(offsetx=offset, width=width)
            offset += width

    def timer_setup(self):
        self.update()
        self.timeout_add(self.update_delay, self.timer_setup)

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.setup_images()

    def _update_popup(self):
        pass

    def update(self):
        icons = self._getkey()
        if icons != self.current_icons:
            self.current_icons = icons
            self.draw()

class Status_Widgets(DefWidget):
    defaults = DefWidget.defaults + [
        ('Bpath', f'{home}/.config/qtile/assets/icons/battery_icon/{color}/{wstyle}'),
        ('Wpath', f'{home}/.config/qtile/assets/icons/wifi_icon/{color}/{wstyle}'),
        ('Vpath', f'{home}/.config/qtile/assets/icons/volume_icon/{color}/{wstyle}'),
        ("interface", wlan),
    ]

    def __init__(self, *args, **kwargs):
        DefWidget.__init__(self, *args, **kwargs)
        self.imgs = self.png(self.Bpath) + self.png(self.Wpath) + self.png(self.Vpath)

    def _getkey(self):
        binfo = psutil.sensors_battery()
        volume = alsaaudio.Mixer(control='Master', device='default')
        quality = iwlib.get_iwconfig(self.interface).get("stats", {}).get("quality")

        keyv = f'volume-{0 if volume is None or volume.getvolume()[0] == 0 or volume.getmute() == 1 else 30 if volume.getvolume()[0] <= 30 else 60 if volume.getvolume()[0] <= 60 else 100}'
        keyw = f'wifi-{"missing" if quality is None else "bad" if quality <= 17 else "medium" if quality <= 35 else "good" if quality <= 52 else "perfect"}'
        keyb = None if binfo is None else (f'battery-{int(binfo.percent / 10)}-charge' if binfo.power_plugged else f'battery-{int(binfo.percent / 10)}')
        return keyw, keyv, keyb