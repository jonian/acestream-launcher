#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Acestream Launcher: Open acestream links with any media player"""

import sys
import time
import hashlib
import argparse
import psutil
import pexpect
import notify2

class AcestreamLauncher(object):
    """Acestream Launcher"""

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='acestream-launcher',
            description='Open acestream links with any media player'
        )
        parser.add_argument(
            'url',
            metavar='URL',
            help='the acestream url to play'
        )
        parser.add_argument(
            '--engine',
            help='the acestream engine command to use (default: system)',
            default='acestreamengine --client-console'
        )
        parser.add_argument(
            '--player',
            help='the media player command to use (default: vlc)',
            default='vlc'
        )

        self.appname = 'Acestream Launcher'
        self.args = parser.parse_args()

        notify2.init(self.appname)
        self.notifier = notify2.Notification(self.appname)

        self.start_acestream()
        self.start_session()
        self.start_player()
        self.close_player()

    def notify(self, message):
        """Show player status notifications"""

        icon = self.args.player
        messages = {
            'running': 'Acestream engine running.',
            'waiting': 'Waiting for channel response...',
            'started': 'Streaming started. Launching player.',
            'noauth': 'Error authenticating to Acestream!',
            'noengine': 'Acstream engine not found in provided path!',
            'unavailable': 'Acestream channel unavailable!'
        }

        print(messages[message])
        self.notifier.update(self.appname, messages[message], icon)
        self.notifier.show()

    def start_acestream(self):
        """Start acestream engine"""

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.kill()

        try:
            self.acestream = psutil.Popen(self.args.engine.split())
            self.notify('running')
            time.sleep(5)
        except FileNotFoundError:
            self.notify('noengine')
            self.close_player(1)

    def start_session(self):
        """Start acestream telnet session"""

        product_key = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
        session = pexpect.spawn('telnet localhost 62062')

        try:
            session.timeout = 10
            session.sendline('HELLOBG version=3')
            session.expect('key=.*')

            request_key = session.after.decode('utf-8').split()[0].split('=')[1]
            signature = (request_key + product_key).encode('utf-8')
            signature = hashlib.sha1(signature).hexdigest()
            response_key = product_key.split('-')[0] + '-' + signature
            pid = self.args.url.split('://')[1]

            session.sendline('READY key=' + response_key)
            session.expect('AUTH.*')
            session.sendline('USERDATA [{"gender": "1"}, {"age": "3"}]')

            self.notify('waiting')
        except (pexpect.TIMEOUT, pexpect.EOF):
            self.notify('noauth')
            self.close_player(1)

        try:
            session.timeout = 30
            session.sendline('START PID ' + pid + ' 0')
            session.expect('http://.*')

            self.session = session
            self.url = session.after.decode('utf-8').split()[0]

            self.notify('started')
        except (pexpect.TIMEOUT, pexpect.EOF):
            self.notify('unavailable')
            self.close_player(1)

    def start_player(self):
        """Start the media player"""

        self.player = psutil.Popen([*self.args.player.split(), self.url])
        self.player.wait()
        self.session.sendline('STOP')
        self.session.sendline('SHUTDOWN')

    def close_player(self, code=0):
        """Close acestream and media player"""

        try:
            self.player.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Media Player not running...')

        try:
            self.acestream.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Acestream not running...')

        sys.exit(code)

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
