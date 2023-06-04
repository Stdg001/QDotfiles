from qtile_extras.widget.mixins import TooltipMixin, ExtendedPopupMixin
from qtile_extras.popup.toolkit import * 
from libqtile.log_utils import logger
from libqtile import bar, widget
from libqtile.widget import base
from libqtile.lazy import lazy
from PIL import Image
from .catppuccin import *
import alsaaudio
import cairocffi
import psutil
import iwlib
import os
import subprocess

home = os.path.expanduser('~')
color = "White"
wstyle = 'White'

bstyle = 'Minimal'
wstyle = 'Minimal'
vstyle = 'Minimal'

proc = subprocess.run('echo /sys/class/net/*/wireless | awk -F"/" "{ print \$5 }"', shell=True, stdout=subprocess.PIPE)
wlan = proc.stdout.decode("utf8").rstrip("\n")

def longNameParse(text): 
    for string in ["Chromium", "Firefox", "Opera", "Visual Studio Code", "Thunar"]: #Add any other apps that have long names here
        if string in text:
            text = string
        else:
            text = text
    return text

class DefWidget(base._TextBox, TooltipMixin, ExtendedPopupMixin):
    
    defaults = [
        ("y_poss", 0, "Modify y possition"),
        ("scale", 1, "Icons size"),
        ('update_delay', 1, 'The delay in seconds between updates'),
        ('spacing', 1, 'Spacing between widgets'),
    ]

    filenames = {}

    def __init__(self, *args, **kwargs):
        base._TextBox.__init__(self, *args, **kwargs)
        TooltipMixin.__init__(self, *args, **kwargs)
        ExtendedPopupMixin.__init__(self, **kwargs)
        self.add_defaults(TooltipMixin.defaults)
        self.add_defaults(self.defaults)
        self.add_defaults(ExtendedPopupMixin.defaults)
        
        self.current_icons = ()
        self.scale = 1.0 / self.scale
        self.length_type = bar.STATIC
        self.length = 0
        self.icon_width = 0  # Añadido: Variable para el ancho del ícono

        self.surfaces = {}

    def png(self, carpeta):
        lista_pngs = []
        for ruta, directorios, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.endswith(".png"):
                    lista_pngs.append((ruta, os.path.splitext(archivo)[0]))
        return lista_pngs

    def timer_setup(self):
        self.update()
        self.timeout_add(self.update_delay, self.timer_setup)

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.setup_images()

    def _update_popup(self):
        pass

    def update(self):
        icons = self._get_icons_key()
        if icons != self.current_icons:
            self.current_icons = icons
            self.draw()

    def draw(self):
        num_icons = len(self.current_icons)
        offset = self.offset
        icon_width = self.icon_width + self.spacing
        self.length = num_icons * icon_width

        for index, key in enumerate(self.current_icons):
            if key == None or key not in self.surfaces:
                continue

            if index > 1: index = 1
            offset = offset + index * icon_width  # Calcula la posición teniendo en cuenta el espaciado
            self.drawer.clear(self.background or self.bar.background)
            self.drawer.ctx.set_source(self.surfaces[key])
            self.drawer.ctx.paint()
            self.drawer.draw(offsetx=offset, width=icon_width)

    def setup_images(self):
        for path, key in self.imgs:
            img_path = f'{path}/{key}.png'
            img = Image.open(img_path)
            input_width, input_height = img.size
            img.close()

            sp = input_height / (self.bar.height - 1)
            width = input_width / sp

            self.icon_width = int(width)
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
            self.surfaces[key] = imgpat

class Status_Widgets(DefWidget):

    defaults = DefWidget.defaults + [
        ('Bpath', f'{home}/.config/qtile/assets/icons/battery_icon/{color}/{vstyle}' , 'Battery Icons Path'),
        ('Wpath', f'{home}/.config/qtile/assets/icons/wifi_icon/{color}/{vstyle}' , 'Wifi Icons Path'),
        ('Vpath', f'{home}/.config/qtile/assets/icons/volume_icon/{color}/{vstyle}' , 'Volume Icons Path'),
        ("interface", wlan, "The interface to monitor"),
    ]

    def __init__(self, *args, **kwargs):
        DefWidget.__init__(self, *args, **kwargs)
        self.imgs = self.png(self.Bpath) + self.png(self.Wpath) + self.png(self.Vpath)

    def _get_icons_key(self):
        binfo = psutil.sensors_battery()
        volume = alsaaudio.Mixer(control='Master', device='default')
        quality = iwlib.get_iwconfig(self.interface).get("stats", {}).get("quality")

        keyv = f'volume-{0 if volume.getvolume()[0] == 0 or volume.getvolume()[0] == None or volume.getmute() == 1 else 30 if volume.getvolume()[0] <= 30 else 60 if volume.getvolume()[0] <= 60 else 100}'
        keyw = f'wifi-{"bad" if quality <= 17 else "medium" if quality <= 35 else "good" if quality <= 52 else "perfect"}'
        if binfo != None:
            keyb = f'battery-{int(binfo.percent / 10)}'
            if binfo and binfo.power_plugged:
                keyb += '-charge'
        else: keyb = None
        return keyw, keyv, keyb