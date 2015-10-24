# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
    python, python-psutil, python-pexpect, python-notify, acestream-engine

## Usage
    acestream-launcher [--host HOST] [--port PORT] [--player PLAYER] URL

## Positional arguments
    URL               The acestream url to play

## Optional arguments
    -h, --help        Show this help message and exit
    --host HOST       The local port to use (default: localhost)
    --port PORT       The player port to use (default: 62062)
    --player PLAYER   The media player to use (default: vlc)
