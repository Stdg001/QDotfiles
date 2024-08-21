import subprocess
import re
import os

home = os.path.expanduser('~')
config = f'{home}/.config/qtile'
supported_cards = ['NVIDIA', 'Intel']
file_source = f'{config}/assets/settings/xorg\ scripts/'

def move(files='', location=''):
    if type(files) == str:
        subprocess.call(f'sudo mv {files} {location}', shell = True)
    elif type(files) == list:
        for i in files:
            subprocess.call(f'sudo mv {i} {location}', shell = True)
            
move(['.zshrc', '.config', '.p10k.zsh'], f'{home}')
move(f'{config}/settings/rofi_grid.rasi', f'{home}/.local/share/rofi/themes')

subprocess.call(f'paru --noconfirm -Syu python-evdev', shell = True)
import evdev

# Search if there is any touchpad and move the drivers
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if "touchpad" in device.name.lower() or "touchpad" in device.phys.lower():
        move(f'{file_source}/50-synaptics.conf', '/etc/X11/xorg.conf.d/')

subprocess.call(f'sudo pacman --noconfirm -Rs python-evdev', shell=True)

# Get GPU
output = subprocess.check_output("lspci | grep -i vga", shell=True).decode("utf-8")
matches = re.findall(r"([^:]*):\s(.*)\[", output)
card_name = matches[0][1].split(" ")[0]

# Verify is the GPU is on the suported cards with their drivers
if card_name in supported_cards:
    if card_name == 'Intel':
        move([f'{file_source}20-modesetting.conf', f'{file_source}20-intel.conf', f'{file_source}modesetting.conf'], '/etc/X11/xorg.conf.d/')
        apps = 'intel-ucode vulkan-intel '

    elif card_name == 'NVIDIA':
        apps = 'nvidia nvidia-utils nvidia-settings '
else: 
    print('\033[93m[WARN] No supported graphic card, you need to install drivers manually\033[00m')
    apps = ''

# See if the divice support bluetooth and install apps
result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
output = result.stdout.lower()
if 'bluetooth' in output and 'soft blocked: no' in output:
    apps += 'blueman bluez-utils pulseaudio-bluetooth '
    services = 'bluetooth'
else: services = ''

# Terminal and apps
apps += 'kitty lsd neofetch bat '

# Fancy apps and utilities
apps += 'rofi pavucontrol lightdm lightdm-gtk-greeter playerctl brightnessctl numlockx scrot dunst '

# Zsh and plugins
apps += 'zsh zsh-autosuggestions zsh-syntax-highlighting zsh-theme-powerlevel10k-git zsh-sudo-git '

# Thunar, plugins and features
apps += 'thunar gvfs xarchiver thunar-archive-plugin '

# Pulseaudio and plugins
apps += 'pulseaudio pulseaudio-alsa pulseaudio-jack '

# Qtile and extras
apps += 'qtile qtile-extras python-psutil python-iwlib python-pyalsaaudio python-netifaces '

# Fonts
apps += 'noto-fonts-cjk noto-fonts-emoji noto-fonts-extra noto-fonts ttf-cascadia-code noto-fonts-emoji ttf-mononoki-nerd ttf-roboto-mono-nerd'

services += 'pulseaudio lightdm'

subprocess.call(f'paru --noconfirm -Syu {apps}', shell = True)
subprocess.call(f'sudo systemctl enable {services}')