# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
```text
python, pyhon-acestream, libnotify, acestream-engine
```

Since `v1.0.0` acestream-launcher uses [Acestream Engine HTTP API](http://wiki.acestream.org/wiki/index.php/Engine_HTTP_API) that is available on acestream-engine `v3.1` or later.

## Usage
```shell
acestream-launcher URL [--player PLAYER] [--engine ENGINE]
```

## Positional arguments
```text
URL                    The acestream url to play
```

## Optional arguments
```text
-h, --help             Show this help message and exit
-p, --player  PLAYER   The media player command to use (default: mpv)
-e, --engine  ENGINE   The engine command to use (default: acestreamengine --client-console)
-t, --timeout TIMEOUT  Time in seconds to wait for stream playback (default: 30)
-v, --verbose          Show engine and media player output in console
```

## Configuration
Create `~/.config/acestream-launcher/config` file to override the default arguments. Use `tty` and `browser` sections to set different options when executing the script from the console or the web browser.

```text
[DEFAULT]
player = vlc
verbose = true
timeout = 60

[tty]
engine = acestreamengine --client-console --log-file /home/jonian/.ACEStream/engine.log

[browser]
engine = acestreamengine --client-gtk --log-file /home/jonian/.ACEStream/browser.log
verbose = false
```

## Requirements
Install required dependencies (compatible with python 2 and 3):

```shell
sudo apt-get install python python-pip
```

Install optional dependencies (support for desktop notifications):

```shell
sudo apt-get install libnotify
```

Install Acestream engine manually (you can find actual links [here](http://wiki.acestream.org/wiki/index.php/Download#Linux) and detailed instructions [here](http://wiki.acestream.org/wiki/index.php/Install_Ubuntu)):

```shell
sudo apt-get install python-setuptools python-m2crypto python-apsw

wget "http://dl.acestream.org/linux/acestream_3.1.16_ubuntu_16.04_x86_64.tar.gz"
tar zxvf acestream_3.1.16_ubuntu_16.04_x86_64.tar.gz
sudo mv acestream_3.1.16_ubuntu_16.04_x86_64 /opt/acestream

wget "http://archive.ubuntu.com/ubuntu/pool/universe/m/m2crypto/m2crypto_0.24.0.orig.tar.xz"
tar xf m2crypto_0.24.0.orig.tar.xz
sudo mv M2Crypto-0.24.0/M2Crypto /opt/acestream/lib/M2Crypto

sudo sed -i "/ROOT=/c\ROOT=\/opt\/acestream" /opt/acestream/start-engine
sudo ln -sf /opt/acestream/start-engine /usr/bin/acestreamengine
```

Install Acestream engine Snap package:

```shell
sudo snap install acestreamplayer
```

## Installation
Install the package with the Python Package Index using `pip` command.

```shell
pip install acestream-launcher
```

## Packages
Arch Linux: [AUR Package](https://aur.archlinux.org/packages/acestream-launcher)  
OpenSUSE: [Build Service](https://build.opensuse.org/project/show/home:drommer:p2pstreams) by [@Drommer](https://github.com/Drommer)

## Browser integration  
Once it is installed, you can set it as default for the `acestream://` links in your browser. Check your browser preferences for default applications.
