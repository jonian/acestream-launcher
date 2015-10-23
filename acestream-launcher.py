#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import time
import psutil
import pexpect
import hashlib
import argparse

class AcestreamLauncher(object):
    """Acestream Launcher: Open acestream links with any media player"""

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='acestream-launcher',
            description='Open acestream links with any media player'
        )
        parser.add_argument(
            'url',
            metavar='URL',
            help='The acestream url to play'
        )
        parser.add_argument(
            '--host',
            help='The host to use (default: localhost)',
            default='localhost'
        )
        parser.add_argument(
            '--port',
            help='The port to use (default: 62062)',
            default='62062'
        )
        parser.add_argument(
            '--player',
            help='The media player to use (default: vlc)',
            default='vlc'
        )

        self.args = parser.parse_args()

        self.start_acestream()
        self.start_session()
        self.start_player()
        self.close_player()

    def start_acestream(self):
        """Start acestream engine"""

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                return

        self.acestream = psutil.Popen(['acestreamengine', '--client-console'])
        time.sleep(5)

    def start_session(self):
        """Start acestream telnet session"""

        session = pexpect.spawn('telnet ' + self.args.host + ' ' + self.args.port)
        session.timeout = 10
        connection = session.expect([pexpect.TIMEOUT, 'Escape character.+'])

        if connection == 0:
            print('Timeout connecting to Acestream...')
            sys.exit(0)

        time.sleep(5)

        try:
            session.sendline('HELLOBG version=3')
            session.expect('key=.* ')

            product_key = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
            request_key = session.after.strip().split('=')[1]
            signature = hashlib.sha1(request_key + product_key).hexdigest()
            response_key = product_key.split('-')[0] + '-' + signature
            pid = self.args.url.split('://')[1]
            session.timeout = 30

            session.sendline('READY key=' + response_key)
            session.expect('AUTH.*')
            session.sendline('USERDATA [{"gender": "1"}, {"age": "3"}]')

            session.sendline('LOAD PID ' + pid)
            session.sendline('START PID ' + pid + ' 0')
            session.expect('http://.* ')

            self.session = session
            self.url = session.after.strip()
        except (pexpect.TIMEOUT):
            print('Timeout connecting to Acestream...')

            self.acestream.terminate()
            sys.exit(0)

    def start_player(self):
        """Start the media player"""

        self.player = psutil.Popen([self.args.player, self.url])
        self.player.wait()
        self.session.sendline('STOP')
        self.session.sendline('SHUTDOWN')

    def close_player(self):
        """Close acestream and media player"""

        try:
            self.player.terminate()
        except (AttributeError, psutil.NoSuchProcess):
            print('Media Player not running...')

        try:
            self.acestream.terminate()
        except (AttributeError, psutil.NoSuchProcess):
            print('Acestream not running...')

        sys.exit(0)

def main():
    """Start Acestream Launcher"""

    try:
        AcestreamLauncher()
    except (KeyboardInterrupt, EOFError):
        print('Acestream Launcher exiting...')

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.terminate()

        sys.exit(0)

main()
