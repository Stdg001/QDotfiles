sudo pacman -Syu tk rofi opera-ffmpeg-codecs visual-studio-code pavucontrol nitrogen pamixer playerctl brightnessctl numlockx scrot feh zathura thunar xarchiver thunar-archive-plugin tumbler glib2 gvfs dunst ttf-cascadia-code noto-fonts-emoji ttf-mononoki-nerd ttf-roboto-mono-nerd lightdm lightdm-gtk-greeter blueman pulseaudio pulseaudio-alsa pulseaudio-bluetooth pulseaudio-jack bluez-utils noto-fonts noto-fonts-cjk noto-fonts-emoji noto-fonts-extra bat zsh dmenu dunst git intel-ucode kitty lsd neofetch zsh-autosuggestions zsh-syntax-highlighting

pip install netifaces scapy iwlib pyxdg pyalsaaudio pillow

paru -Sqyu zsh-theme-powerlevel10k-git zsh-sudo-git qtile-git qimgv-git picom-jonaburg-git 

sudo systemctl --user enable pulseaudio
sudo systemctl enable bluetooth.service