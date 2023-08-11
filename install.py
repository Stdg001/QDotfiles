import evdev
import subprocess
import re
import os

home = os.path.expanduser('~')
config = f'{home}/.config/qtile'
supported_cards = ['NVIDIA', 'Intel']

def touchpad_connected():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "touchpad" in device.name.lower() or "touchpad" in device.phys.lower():
            return True
    return False

def graphics_card():
    command = "lspci | grep -i vga"
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    pattern = r"([^:]*):\s(.*)\["
    matches = re.findall(pattern, output)
    card_name = matches[0][1].split(" ")[0]
    return card_name

def install_package(package = '', AUR = False):
    if AUR:
        subprocess.call(f'yay -Syu {package}', shell= True)
    else:
        subprocess.call(f'sudo pacman -Syu {package}', shell= True)

def install_AUR():
    subprocess.call('')

def check_bluetooth():
    result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
    output = result.stdout.lower()
    if 'bluetooth' in output and 'soft blocked: no' in output:
        return True
    else:
        return False

def move(name='', location=''):
    subprocess.call(f'sudo mv {name} {location}', shell=True)

move('.config', f'{home}')
move('.p10k.zsh', f'{home}')
move('.zshrc', f'{home}')

if touchpad_connected():
    move(f'{config}/assets/settings/xorg\ scripts/50-synaptics.conf', '/etc/X11/xorg.conf.d/')

graphic_card = graphics_card()
if graphic_card in supported_cards:
    if graphic_card == 'Intel':
        move(f'{config}/assets/settings/xorg\ scripts/20-intel.conf', '/etc/X11/xorg.conf.d/')
        move(f'{config}/assets/settings/xorg\ scripts/20-modesetting.conf', '/etc/X11/xorg.conf.d/')
        move(f'{config}/assets/settings/xorg\ scripts/modesetting.conf', '/etc/X11/xorg.conf.d/')
        install_package('intel-ucode vulkan-intel')

    elif graphic_card == 'NVIDIA':
        install_package('nvidia nvidia-utils nvidia-settings')
else: print('\033[93m[WARN] No supported graphic card, you need to install drivers manually\033[00m')

install_package('rofi python-psutil pavucontrol nitrogen github-cli noto-fonts-cjk gvfs zsh-autosuggestions zsh-syntax-highlighting noto-fonts-emoji noto-fonts-extra bat zsh dmenu dunst git kitty lsd neofetch pulseaudio pulseaudio-alsa pulseaudio-jack noto-fonts playerctl lightdm lightdm-gtk-greeter brightnessctl numlockx scrot zathura thunar xarchiver dunst ttf-cascadia-code noto-fonts-emoji ttf-mononoki-nerd ttf-roboto-mono-nerd thunar-archive-plugin glib2')
install_package('zsh-theme-powerlevel10k-git zsh-sudo-git qimgv-git picom-jonaburg-git', True)
subprocess.call('sudo systemctl --user enable pulseaudio', shell=True)
move(f'{config}/settings/rofi_grid.rasi', f'{home}/.local/share/rofi/themes')

if check_bluetooth():
    install_package('blueman bluez-utils pulseaudio-bluetooth')
    subprocess.call('sudo systemctl enable bluetooth.service', shell=True)