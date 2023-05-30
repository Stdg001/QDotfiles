#!/bin/sh
#xrandr --output eDP1 --primary --mode 1920x1080 --rotate normal --output HDMI1 --mode 1366x768 --rotate normal --right-of eDP1
keybLayout=$(setxkbmap es)

$config = $HOME + '/.config/qtile/'

xrandr --output eDP-1 --primary --auto --rotate normal --output HDMI-1 --auto --rotate normal --right-of eDP-1

nitrogen --restore &
numlockx &
dunst -config $HOME/.config/qtile/assets/settings/dunstrc &
picom --config $HOME/.config/qtile/assets/settings/picom.conf &