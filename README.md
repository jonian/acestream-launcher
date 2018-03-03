# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
    python, curl, libnotify, acestream-engine

Since `v1.0.0` acestream-launcher uses [Acestream Engine HTTP API](http://wiki.acestream.org/wiki/index.php/Engine_HTTP_API) that is available on acestream-engine `v3.1` or later.

## Usage
    acestream-launcher URL [--player PLAYER] [--engine ENGINE]

## Positional arguments
    URL                   The acestream url to play

## Optional arguments
    -h, --help            Show this help message and exit
    -p, --player PLAYER   The media player command to use (default: mpv)
    -e, --engine ENGINE   The engine command to use (default: acestreamengine --client-console)

## Installation
Install required dependencies and run `install.sh` as root. The script will install acestream-launcher in `opt` directory.

## Packages
Arch Linux: [AUR Package](https://aur.archlinux.org/packages/acestream-launcher)
