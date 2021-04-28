# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
```text
python, pyhon-acestream, libnotify, acestream-engine
```

Since `v1.0.0` acestream-launcher uses [Acestream Engine HTTP API](https://wiki.acestream.media/Engine_HTTP_API) that is available on acestream-engine `v3.1` or later.

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
-l, --hls              Get HLS stream instead of HTTP stream
-v, --verbose          Show engine and media player output in console
```

## Configuration
Create `~/.config/acestream-launcher/config` file to override the default arguments. Use `tty` and `browser` sections to set different options when executing the script from the console or the web browser.

```text
[DEFAULT]
player = vlc
verbose = true
timeout = 60
host = 127.0.0.1
port = 6878

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

Install Acestream engine manually (you can find actual links [here](https://wiki.acestream.media/Download#Linux) and detailed instructions [here](https://wiki.acestream.media/Install_Ubuntu)):

```shell
sudo apt-get install python-setuptools python-m2crypto python-apsw

wget "http://download.acestream.media/linux/acestream_3.1.49_ubuntu_18.04_x86_64.tar.gz"
tar zxvf acestream_3.1.49_ubuntu_18.04_x86_64.tar.gz
sudo mv acestream_3.1.49_ubuntu_18.04_x86_64 /opt/acestream

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
