#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import time
import psutil
import pexpect
import hashlib
import pynotify
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
            '--client',
            help='The acestream engine client to use (default: console)',
            default='console'
        )
        parser.add_argument(
            '--player',
            help='The media player to use (default: vlc)',
            default='vlc'
        )

        self.args = parser.parse_args()

        self.appname = 'Acestream Launcher'
        self.icon = self.args.player
        self.messages = {
            'running': 'Acestream engine running.',
            'waiting': 'Waiting for channel response...',
            'started': 'Streaming started. Launching player.',
            'noauth': 'Error authenticating to Acestream!',
            'unavailable': 'Acestream channel unavailable!',
            'terminated': 'Acestream engine terminated.'
        }

        pynotify.init(self.appname)
        self.notifier = pynotify.Notification(self.appname)

        self.start_acestream()
        self.start_session()
        self.start_player()
        self.close_player()

    def start_acestream(self):
        """Start acestream engine"""

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.kill()

        self.acestream = psutil.Popen(['acestreamengine', '--client-' + self.args.client])
        self.notifier.update(self.appname, self.messages['running'], self.icon)
        self.notifier.show()

        time.sleep(5)

    def start_session(self):
        """Start acestream telnet session"""

        product_key = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
        session = pexpect.spawn('telnet localhost 62062')

        try:
            session.timeout = 5
            session.sendline('HELLOBG version=3')
            session.expect('key=.*')

            request_key = session.after.split()[0].split('=')[1]
            signature = hashlib.sha1(request_key + product_key).hexdigest()
            response_key = product_key.split('-')[0] + '-' + signature
            pid = self.args.url.split('://')[1]

            session.sendline('READY key=' + response_key)
            session.expect('AUTH.*')
            session.sendline('USERDATA [{"gender": "1"}, {"age": "3"}]')

            self.notifier.update(self.appname, self.messages['waiting'], self.icon)
            self.notifier.show()
        except (pexpect.TIMEOUT, pexpect.EOF):
            print('Error authenticating to Acestream...')
            self.notifier.update(self.appname, self.messages['noauth'], self.icon)
            self.notifier.show()

            self.acestream.kill()
            sys.exit(1)

        try:
            session.timeout = 30
            session.sendline('START PID ' + pid + ' 0')
            session.expect('http://.*')

            self.session = session
            self.url = session.after.split()[0]

            self.notifier.update(self.appname, self.messages['started'], self.icon)
            self.notifier.show()
        except (pexpect.TIMEOUT, pexpect.EOF):
            print('Acestream channel unavailable...')
            self.notifier.update(self.appname, self.messages['unavailable'], self.icon)
            self.notifier.show()

            self.acestream.kill()
            sys.exit(1)

    def start_player(self):
        """Start the media player"""

        self.player = psutil.Popen([self.args.player, self.url])
        self.player.wait()
        self.session.sendline('STOP')
        self.session.sendline('SHUTDOWN')

    def close_player(self):
        """Close acestream and media player"""

        try:
            self.player.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Media Player not running...')

        try:
            self.acestream.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Acestream not running...')

        self.notifier.update(self.appname, self.messages['terminated'], self.icon)
        self.notifier.show()

        sys.exit(0)

def main():
    """Start Acestream Launcher"""

    try:
        AcestreamLauncher()
    except (KeyboardInterrupt, EOFError):
        print('Acestream Launcher exiting...')

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.kill()

        sys.exit(0)

main()
