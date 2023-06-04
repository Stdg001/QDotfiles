import os
import alsaaudio
import psutil
import iwlib
import subprocess
from PIL import Image
import cairocffi
from libqtile.log_utils import logger
from libqtile import bar, widget
from libqtile.widget import base
from libqtile.lazy import lazy
from qtile_extras.widget.mixins import TooltipMixin, ExtendedPopupMixin
from qtile_extras.popup.toolkit import *

home = os.path.expanduser('~')

proc = subprocess.run('echo /sys/class/net/*/wireless | awk -F"/" "{ print \$5 }"', shell=True, capture_output=True, text=True)
wlan = proc.stdout.strip()

color = "White"
wstyle = 'Minimal'

def longNameParse(text): 
    for string in ["Chromium", 'GIMP', "Firefox", "Opera", "Visual Studio Code", "Thunar"]: #Add any other apps that have long names here
        if string in text:
            text = string
        else:
            text = text
    return text

class DefWidget(base._TextBox, TooltipMixin, ExtendedPopupMixin):
    defaults = [
        ("y_poss", 0, "Modify y position"),
        ("scale", 1, "Icons size"),
        ('update_delay', 1, 'The delay in seconds between updates'),
        ('spacing', 1, 'Spacing between widgets'),
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
        self.length = 0
        self.icon_width = 0

        self.current_icons = ()
        self.surfaces = {}

    def png(self, carpeta):
        lista_pngs = []
        for ruta, directorios, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.endswith(".png"):
                    lista_pngs.append((ruta, os.path.splitext(archivo)[0]))
        return lista_pngs

    def setup_images(self):
        for path, key in self.imgs:
            img_path = f'{path}/{key}.png'
            img = Image.open(img_path)
            input_width, input_height = img.size
            img.close()
            sp = input_height / (self.bar.height - 1)
            width = input_width / sp
            img = cairocffi.ImageSurface.create_from_png(img_path)
            imgpat = cairocffi.SurfacePattern(img)
            scaler = cairocffi.Matrix()
            scaler.scale(sp, sp)
            scaler.scale(self.scale, self.scale)
            factor = (1 - 1 / self.scale) / 2
            scaler.translate(-width * factor, -width * factor)
            scaler.translate(self.actual_padding * -1, self.y_poss)
            imgpat.set_matrix(scaler)
            imgpat.set_filter(cairocffi.FILTER_BEST)
            self.surfaces[key] = imgpat, int(width)

    def draw(self):
        offset = self.offset
        total_width = 0

        for index, key in enumerate(self.current_icons):
            if key == None or key not in self.surfaces: continue
            if index > 1: index = 1

            surface, width = self.surfaces[key]
            total_width = total_width + width
            
            logger.warn(total_width)
            self.length = total_width

            icon_width = width + self.spacing

            offset = offset + index * icon_width
            self.drawer.clear(self.background or self.bar.background)
            self.drawer.ctx.set_source(surface)
            self.drawer.ctx.paint()
            self.drawer.draw(offsetx=offset, width=icon_width)

    def timer_setup(self):
        self.update()
        self.timeout_add(self.update_delay, self.timer_setup)

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.setup_images()

    def _update_popup(self): pass

    def update(self):
        icons = self._getkey()
        if self._getkey() != self.current_icons:
            self.current_icons = icons
            self.draw() 

class Status_Widgets(DefWidget):
    defaults = DefWidget.defaults + [
        ('Bpath', f'{home}/.config/qtile/assets/icons/battery_icon/{color}/{wstyle}' , 'Battery Icons Path'),
        ('Wpath', f'{home}/.config/qtile/assets/icons/wifi_icon/{color}/{wstyle}' , 'Wifi Icons Path'),
        ('Vpath', f'{home}/.config/qtile/assets/icons/volume_icon/{color}/{wstyle}' , 'Volume Icons Path'),
        ("interface", wlan, "The interface to monitor")]

    def __init__(self, *args, **kwargs):
        DefWidget.__init__(self, *args, **kwargs)
        self.imgs = self.png(self.Bpath) + self.png(self.Wpath) + self.png(self.Vpath)

    def _getkey(self):
        binfo = psutil.sensors_battery()
        volume = alsaaudio.Mixer(control='Master', device='default')
        quality = iwlib.get_iwconfig(self.interface).get("stats", {}).get("quality")

        keyv = f'volume-{0 if volume == None or volume.getvolume()[0] == 0 or volume.getmute() == 1 else 30 if volume.getvolume()[0] <= 30 else 60 if volume.getvolume()[0] <= 60 else 100}'
        keyw = f'wifi-{"missing" if quality == None else "bad" if quality <= 17 else "medium" if quality <= 35 else "good" if quality <= 52 else "perfect"}'
        keyb = None if binfo is None else (f'battery-{int(binfo.percent / 10)}-charge' if binfo.power_plugged else f'battery-{int(binfo.percent / 10)}')
        return keyw, keyv, keyb