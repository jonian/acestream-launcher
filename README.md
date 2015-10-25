# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
    python, python-psutil, python-pexpect, python-notify, acestream-engine

## Usage
acestream-launcher URL [--player PLAYER] [--client CLIENT] [--download-limit LIMIT] [--upload-limit LIMIT]

## Positional arguments
    URL                      The acestream url to play

## Optional arguments
    -h, --help               Show this help message and exit
    --player PLAYER          The media player to use (default: vlc)
    --client CLIENT          The acestream engine client to use (default: console)
    --download-limit LIMIT   Download limit in Kb/s (default: 1000)
    --upload-limit LIMIT     Upload limit in Kb/s (default: 40)
