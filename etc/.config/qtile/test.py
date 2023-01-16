import iwlib
import cv2
import numpy as np
from libqtile.widget import base

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

