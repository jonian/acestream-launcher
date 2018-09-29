# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
    python, libnotify, acestream-engine

Since `v1.0.0` acestream-launcher uses [Acestream Engine HTTP API](http://wiki.acestream.org/wiki/index.php/Engine_HTTP_API) that is available on acestream-engine `v3.1` or later.

## Usage
    acestream-launcher URL [--player PLAYER] [--engine ENGINE]

## Positional arguments
    URL                   The acestream url to play

## Optional arguments
    -h, --help            Show this help message and exit
    -p, --player PLAYER   The media player command to use (default: mpv)
    -e, --engine ENGINE   The engine command to use (default: acestreamengine --client-console)
    -v, --verbose         Show engine and media player output in console

## Installation
Install required dependencies and run `install.sh` as root. The script will install acestream-launcher in `opt` directory.

## Packages
Arch Linux: [AUR Package](https://aur.archlinux.org/packages/acestream-launcher)  
OpenSUSE: [Build Service](https://build.opensuse.org/package/show/home:drommer/acestream-launcher) by [@Drommer](https://github.com/Drommer)
