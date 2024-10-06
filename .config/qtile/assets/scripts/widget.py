import alsaaudio
import psutil
import iwlib
import cairocffi
from libqtile import bar
from libqtile.widget import base
import netifaces
import glob
import os

from libqtile.log_utils import logger

home = os.path.expanduser('~')
wlan = netifaces.gateways()['default'][netifaces.AF_INET][1]

color = "White"
wstyle = 'Minimal'

def get_dimensions(filename):
    with open(filename, 'rb') as f:
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("No es un archivo PNG")
        
        f.read(4)
        chunk_type = f.read(4)
        if chunk_type != b'IHDR':
            raise ValueError("No se encontró el chunk IHDR")
        
        height = int.from_bytes(f.read(4), 'big')
        width = int.from_bytes(f.read(4), 'big')
        
        return width, height

def longNameParse(text):
    long_names = ["Chromium", 'GIMP', "Firefox", "Opera", "Visual Studio Code", "Thunar", "LibreOffice"]
    return next((name for name in long_names if name in text), text)

class DefWidget(base._TextBox):
    defaults = [
        # ('padding', 1, 'Modify padding'),
        ("y_poss", 0, "Modify y position"),
        ("scale", 1, "Icons size"),
        ('update_delay', 1, 'The delay in seconds between updates'),
    ]

    def __init__(self, *args, **kwargs):
        base._TextBox.__init__(self, *args, **kwargs)
        self.add_defaults(self.defaults)

        self.scale = 1.0 / self.scale
        self.length_type = bar.STATIC
        self.icon_width = 0

        self.current_icons = ()
        self.surfaces = {}

    def png(self, folder):
        return [
            (os.path.dirname(path), os.path.splitext(os.path.basename(path))[0])
            for path in glob.glob(os.path.join(folder, "*.png"))
        ]

    def setup_images(self):
        max_icon_size = self.bar.height - 1
        
        for path, key in self.imgs:
            img_path = os.path.join(path, f'{key}.png')
            input_height, input_width = get_dimensions(img_path)

            scale_factor = min(max_icon_size / input_height, max_icon_size / input_width)
            scaled_height = input_height * scale_factor
            scaled_width = input_width * scale_factor

            img = cairocffi.ImageSurface.create_from_png(img_path)
            imgpat = cairocffi.SurfacePattern(img)

            scaler = cairocffi.Matrix()
            scaler.scale(input_width / scaled_width, input_height / scaled_height)
            scaler.scale(self.scale, self.scale)

            factor = (1 - 1 / self.scale) / 2
            scaler.translate(-scaled_width * factor, -scaled_width * factor)

            y_offset = (self.bar.height - scaled_height) / 2
            scaler.translate(self.padding - 1, self.y_poss - y_offset)

            imgpat.set_matrix(scaler)
            imgpat.set_filter(cairocffi.FILTER_BEST)
            
            self.surfaces[key] = imgpat, int(scaled_width)


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

    def update(self):
        icons = self._getkey()
        if icons != self.current_icons:
            self.current_icons = icons
            self.draw()

class Status_Widgets(base.InLoopPollText):
    defaults = DefWidget.defaults + [
        ('size', 30, 'Icon size'),
        ('update_interval', .1, 'The delay in seconds between updates'),
        ("interface", wlan),
    ] 

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(self.defaults)
        
        self.fontsize = self.size
        self.font = 'Material Symbols Outlined'

    def tick(self):
        self.update(self.poll())
        return self.update_interval
    
    def poll(self):
        binfo = psutil.sensors_battery()
        volume = alsaaudio.Mixer(control='Master', device='default')
        quality = iwlib.get_iwconfig(self.interface).get("stats", {}).get("quality")

        wicons = ['', '', '', '', '', '']
        vicons = ['','', '', '']
        bicons = ['', '', '', '', '', '']
        
        w = wicons[(0 if quality is None else 1 if quality <= 14 else 2 if quality <= 28 else 3 if quality <= 42 else 4 if quality <= 56 else 5)]
        v = vicons[(0 if volume is None or volume.getvolume()[0] == 0 or volume.getmute() == 1 else 1 if volume.getvolume()[0] <= 30 else 2 if volume.getvolume()[0] <= 60 else 3)]
        b = '' if binfo is None else bicons[(0 if None else None)]
        return f'{w}{v}{b}'
