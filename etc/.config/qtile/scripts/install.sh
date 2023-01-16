sudo pacman -S bat dmenu code dunst git intel-ucode kitty lsd neofetch qtile python-gimp spotify unzip zip wget zsh zsh-autosuggestions zsh-syntax-highlighting

mkdir $HOME/.repos
cd !$
git clone https://aur.archlinux.org/paru-bin.git
cd paru-bin
makepkg -si

paru -S spotify

git clone 