
import re
import subprocess

from libqtile import bar
from libqtile.command.base import expose_command
from libqtile.widget import base

__all__ = [
    "Volume",
]

re_vol = re.compile(r"(\d?\d?\d?)%")


class Volume(base._TextBox):
    """Widget that display and change volume

    By default, this widget uses ``amixer`` to get and set the volume so users
    will need to make sure this is installed. Alternatively, users may set the
    relevant parameters for the widget to use a different application.

    If theme_path is set it draw widget as icons.
    """

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("cardid", None, "Card Id"),
        ("device", "default", "Device Name"),
        ("channel", "Master", "Channel"),
        ("padding", 3, "Padding left and right. Calculated if None."),
        ("update_interval", 0.2, "Update time in seconds."),
        ("theme_path", None, "Path of the icons"),
        (
            "emoji",
            False,
            "Use emoji to display volume states, only if ``theme_path`` is not set."
            "The specified font needs to contain the correct unicode characters.",
        ),
        ("mute_command", None, "Mute command"),
        ("volume_app", None, "App to control volume"),
        ("volume_up_command", None, "Volume up command"),
        ("volume_down_command", None, "Volume down command"),
        (
            "get_volume_command",
            None,
            "Command to get the current volume. "
            "The expected output should include 1-3 numbers and a ``%`` sign.",
        ),
        ("check_mute_command", None, "Command to check mute status"),
        (
            "check_mute_string",
            "[off]",
            "String expected from check_mute_command when volume is muted."
            "When the output of the command matches this string, the"
            "audio source is treated as muted.",
        ),
        (
            "step",
            2,
            "Volume change for up an down commands in percentage."
            "Only used if ``volume_up_command`` and ``volume_down_command`` are not set.",
        ),
    ]

    def __init__(self, **config):
        base._TextBox.__init__(self, "0", **config)
        self.add_defaults(Volume.defaults)
        self.surfaces = {}
        self.volume = None

        self.add_callbacks(
            {
                "Button1": self.mute,
                "Button3": self.run_app,
                "Button4": self.increase_vol,
                "Button5": self.decrease_vol,
            }
        )

    def _configure(self, qtile, parent_bar):
        if self.theme_path:
            self.length_type = bar.STATIC
            self.length = 0
        base._TextBox._configure(self, qtile, parent_bar)

    def timer_setup(self):
        self.timeout_add(self.update_interval, self.update)
        if self.theme_path:
            self.setup_images()

    def create_amixer_command(self, *args):
        cmd = ["amixer"]

        if self.cardid is not None:
            cmd.extend(["-c", str(self.cardid)])

        if self.device is not None:
            cmd.extend(["-D", str(self.device)])

        cmd.extend([x for x in args])
        return subprocess.list2cmdline(cmd)

    def button_press(self, x, y, button):
        base._TextBox.button_press(self, x, y, button)
        self.draw()

    def update(self):
        vol = self.get_volume()
        if vol != self.volume:
            self.volume = vol
            # Update the underlying canvas size before actually attempting
            # to figure out how big it is and draw it.
            self._update_drawer()
            self.bar.draw()
        self.timeout_add(self.update_interval, self.update)

    def _update_drawer(self):
        if self.theme_path:
            self.drawer.clear(self.background or self.bar.background)
            if self.volume <= 0:
                img_name = "audio-volume-muted"
            elif self.volume <= 30:
                img_name = "audio-volume-low"
            elif self.volume < 80:
                img_name = "audio-volume-medium"
            else:  # self.volume >= 80:
                img_name = "audio-volume-high"

            self.drawer.ctx.set_source(self.surfaces[img_name])
            self.drawer.ctx.paint()
        elif self.emoji:
            if self.volume <= 0:
                self.text = "\U0001f507"
            elif self.volume <= 30:
                self.text = "\U0001f508"
            elif self.volume < 80:
                self.text = "\U0001f509"
            elif self.volume >= 80:
                self.text = "\U0001f50a"
        else:
            if self.volume == -1:
                self.text = "M"
            else:
                self.text = "{}%".format(self.volume)

    def setup_images(self):
        from libqtile import images

        names = (
            "audio-volume-high",
            "audio-volume-low",
            "audio-volume-medium",
            "audio-volume-muted",
        )
        
        d_images = images.Loader(self.theme_path)(*names)
        for name, img in d_images.items():
            new_height = self.bar.height - 1
            img.resize(height=new_height)
            if img.width > self.length:
                self.length = img.width + self.actual_padding * 2
            self.surfaces[name] = img.pattern

    def get_volume(self):
        try:
            if self.get_volume_command is not None:
                get_volume_cmd = self.get_volume_command
            else:
                get_volume_cmd = self.create_amixer_command("sget", self.channel)

            mixer_out = subprocess.getoutput(get_volume_cmd)
        except subprocess.CalledProcessError:
            return -1

        check_mute = mixer_out
        if self.check_mute_command:
            check_mute = subprocess.getoutput(self.check_mute_command)

        if self.check_mute_string in check_mute:
            return -1

        volgroups = re_vol.search(mixer_out)
        if volgroups:
            return int(volgroups.groups()[0])
        else:
            # this shouldn't happen
            return -1

    def draw(self):
        if self.theme_path:
            self.drawer.draw(offsetx=self.offset, offsety=self.offsety, width=self.length)
        else:
            base._TextBox.draw(self)

    @expose_command()
    def increase_vol(self):
        if self.volume_up_command is not None:
            volume_up_cmd = self.volume_up_command
        else:
            volume_up_cmd = self.create_amixer_command(
                "-q", "sset", self.channel, "{}%+".format(self.step)
            )

        subprocess.call(volume_up_cmd, shell=True)


    @expose_command()
    def decrease_vol(self):
        if self.volume_down_command is not None:
            volume_down_cmd = self.volume_down_command
        else:
            volume_down_cmd = self.create_amixer_command(
                "-q", "sset", self.channel, "{}%-".format(self.step)
            )

        subprocess.call(volume_down_cmd, shell=True)


    @expose_command()
    def mute(self):
        if self.mute_command is not None:
            mute_cmd = self.mute_command
        else:
            mute_cmd = self.create_amixer_command("-q", "sset", self.channel, "toggle")

        subprocess.call(mute_cmd, shell=True)


    @expose_command()
    def run_app(self):
        if self.volume_app is not None:
            subprocess.Popen(self.volume_app, shell=True)
