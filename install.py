import subprocess
import re
import os

home = os.path.expanduser('~')
config = f'{home}/.config/qtile'
supported_cards = ['NVIDIA', 'Intel']

def install_package(package = '', AUR = False):
    if AUR:
        subprocess.call(f'paru --noconfirm -Syu {package}', shell= True)
    else:
        subprocess.call(f'sudo pacman --noconfirm -Syu {package}', shell= True)

def touchpad_connected():
    install_package('python-evdev')
    import evdev
    
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "touchpad" in device.name.lower() or "touchpad" in device.phys.lower():
            return True
    return False

def graphics_card():
    output = subprocess.check_output("lspci | grep -i vga", shell=True).decode("utf-8")
    matches = re.findall(r"([^:]*):\s(.*)\[", output)
    card_name = matches[0][1].split(" ")[0]
    return card_name

def check_bluetooth():
    result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
    output = result.stdout.lower()
    if 'bluetooth' in output and 'soft blocked: no' in output:
        return True
    else:
        return False

def move(files='', location=''):
    if type(files) == str:
        print(f"file:{files}, destination:{location}")

    elif type(files) == list:
        for i in files:
            print(f"file:{i}, destination:{location}")
            
move(['.zshrc', '.config', '.p10k.zsh'], f'{home}')

if touchpad_connected():
    move(f'{config}/assets/settings/xorg\ scripts/50-synaptics.conf', '/etc/X11/xorg.conf.d/')

graphic_card = graphics_card()
if graphic_card in supported_cards:
    if graphic_card == 'Intel':
        file_source = f'{config}/assets/settings/xorg\ scripts/'
        move([f'{file_source}20-modesetting.conf', f'{file_source}20-intel.conf', f'{file_source}modesetting.conf'], '/etc/X11/xorg.conf.d/')
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
