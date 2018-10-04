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
Install required dependencies: 
`sudo apt-get install python libnotify`

Install acestream-launcher:  
`git clone https://github.com/thepante/acestream-launcher.git`  
`cd acestream-launcher`  
`sudo ./install.sh`  

The script will install acestream-launcher in `/opt` directory.

## Packages
Arch Linux: [AUR Package](https://aur.archlinux.org/packages/acestream-launcher)  
OpenSUSE: [Build Service](https://build.opensuse.org/package/show/home:drommer/acestream-launcher) by [@Drommer](https://github.com/Drommer)  

## Integrate it with your browser  
Now that you installed this launcher, you can set it as default for the `acestream://` links. Check your browser preferences for default applications. 
