# Acestream Launcher
Acestream Launcher allows you to open Acestream links with a Media Player of your choice

## Dependencies
    python, python-psutil, python-pexpect, python-notify2, acestream-engine

## Usage
    acestream-launcher URL [--client CLIENT] [--player PLAYER] [--engine-path PATH] [--lib-path PATH]

## Positional arguments
    URL               The acestream url to play

## Optional arguments
    -h, --help                  Show this help message and exit
    --client CLIENT             The acestream engine client to use (default: console)
    --player PLAYER             The media player to use (default: vlc)
    --engine-path ENGINE_PATH   The acestream engine executable to use (default: system)
    --lib-path LIB_PATH         The acestream engine library path to use (default: system)
