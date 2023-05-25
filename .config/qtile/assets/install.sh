sudo pacman -Syu tk noto-fonts noto-fonts-cjk noto-fonts-emoji noto-fonts-extra bat zsh dmenu dunst git intel-ucode kitty lsd neofetch zsh-autosuggestions zsh-syntax-highlighting
pip install netifaces scapy iwlib pyxdg alsaaudio

cd $HOME/.repos
git clone https://aur.archlinux.org/paru-bin.git
cd paru-bin
makepkg -si

paru -Syu zsh-theme-powerlevel10k-git spotify code-git zsh-sudo-git qtile-git rofi pavucontrol nitrogen pamixer playerctl brightnessctl numlockx scrot feh zathura qimgv-git picom-jonaburg-git thunar xarchiver thunar-archive-plugin tumbler glib2 gvfs dunst ttf-cascadia-code noto-fonts-emoji ttf-mononoki-nerd ttf-roboto-mono-nerd lightdm lightdm-gtk-greetern