sudo pacman -S bat zsh dmenu python-iwlib code dunst git intel-ucode kitty lsd neofetch qtile p7zip wget zsh-autosuggestions zsh-syntax-highlighting

mkdir $HOME/.repos
cd !$

git clone https://aur.archlinux.org/paru-bin.git
cd paru-bin
makepkg -si

pip install --no-input netifaces python-nmap scapy

paru -Sy --noconfirm zsh-theme-powerlevel10k-git spotify code-git zsh-sudo-git qtile-git
echo 'source /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme' >> ~/.zshrc