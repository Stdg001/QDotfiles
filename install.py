import subprocess
import re
import os
import shutil
import argparse

# Define las rutas de los archivos y directorios
HOME = os.path.expanduser('~')
CONFIG = f'{HOME}/.config/qtile'
FILE_SOURCE = f'{CONFIG}/assets/settings/xorg/scripts/'

# Define las tarjetas gráficas compatibles
SUPPORTED_CARDS = ['NVIDIA', 'Intel']

# Define las aplicaciones a instalar
APPS = [
    'kitty', 'lsd', 'neofetch', 'bat',
    'rofi', 'pavucontrol', 'lightdm', 'lightdm-gtk-greeter', 'playerctl', 'brightnessctl', 'numlockx', 'scrot', 'dunst',
    'zsh', 'zsh-autosuggestions', 'zsh-syntax-highlighting', 'zsh-theme-powerlevel10k-git', 'zsh-sudo-git',
    'thunar', 'gvfs', 'xarchiver', 'thunar-archive-plugin',
    'pulseaudio', 'pulseaudio-alsa', 'pulseaudio-jack',
    'qtile', 'qtile-extras', 'python-psutil', 'python-iwlib', 'python-pyalsaaudio', 'python-netifaces', 'python-dbus-next', 'python-pyxdg'
    'noto-fonts-cjk', 'noto-fonts-emoji', 'noto-fonts-extra', 'noto-fonts', 'ttf-cascadia-code', 'noto-fonts-emoji', 'ttf-mononoki-nerd', 'ttf-roboto-mono-nerd'
]

# Define los servicios a habilitar
SERVICES = ['pulseaudio', 'lightdm']

# Define una función para mover archivos
def move_files(files, location=''):
    if isinstance(files, str):
        shutil.move(files, location)
    elif isinstance(files, list):
        for file in files:
            shutil.move(file, location)

def main():
    # Crea un objeto ArgumentParser
    parser = argparse.ArgumentParser(description="Instalador de paquetes y configurador de sistema.")

    # Define argumentos opcionales para desactivar acciones
    parser.add_argument("--no-move-files", action="store_false", help="Desactiva el movimiento de archivos de configuración.")
    parser.add_argument("--no-gpu", action="store_false", help="Desactiva la configuración de la tarjeta gráfica.")
    parser.add_argument("--no-bluetooth", action="store_false", help="Desactiva la configuración de Bluetooth.")
    parser.add_argument("--no-hardware-drivers", action="store_false", help="Desactiva la configuracion del hardware")

    # Analiza los argumentos
    args = parser.parse_args()

    if args.no_move_files is not False:
        # Mueve los archivos de configuración
        move_files(['.zshrc', '.config', '.p10k.zsh'], HOME)
        move_files(f'{CONFIG}/assets/settings/rofi_grid.rasi', f'{HOME}/.local/share/rofi/themes')

    if args.no_hardware_drivers is not False:
        subprocess.call(f'paru --noconfirm -S python-evdev', shell=True)
        from evdev import InputDevice, list_devices

        # Busca el touchpad y mueve los controladores
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if "touchpad" in device.name.lower() or "touchpad" in device.phys.lower():
                move_files(f'{FILE_SOURCE}/50-synaptics.conf', '/etc/X11/xorg.conf.d/')

        subprocess.call(f'sudo pacman --noconfirm -Rs python-evdev', shell=True)
        
        if args.no_bluetooth is not False:
            # Verifica si el dispositivo admite Bluetooth
            result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
            output = result.stdout.lower()
            if 'bluetooth' in output and 'soft blocked: no' in output:
                APPS.extend(['blueman', 'bluez-utils', 'pulseaudio-bluetooth'])
                SERVICES.append('bluetooth')

    if args.gpu_drivers is not False:
        output = subprocess.check_output("lspci | grep -i vga", shell=True).decode("utf-8")
        matches = re.findall(r"([^:]*):\s(.*)\[", output)
        card_name = matches[0][1].split(" ")[0]
        
        if card_name == 'Intel':
            move_files([f'{FILE_SOURCE}20-modesetting.conf', f'{FILE_SOURCE}modesetting.conf'], '/etc/X11/xorg.conf.d/')  # , f'{FILE_SOURCE}20-intel.conf'
            APPS.extend(['mesa', 'intel-ucode', 'vulkan-intel', ''])
        
        elif card_name == 'NVIDIA':
            APPS.extend(['nvidia', 'nvidia-utils', 'nvidia-settings'])

    # Instala las aplicaciones
    subprocess.call(f'paru --noconfirm -Syu {" ".join(APPS)}', shell=True)

    # Habilita los servicios
    subprocess.call(f'sudo systemctl enable {" ".join(SERVICES)}', shell=True)

    print('Arch succesfull configurated')
if __name__ == "__main__":
    main()
