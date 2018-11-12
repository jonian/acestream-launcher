#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Acestream Launcher: Open acestream links with any media player"""

import os
import sys
import argparse
import subprocess

try:
  import configparser
except ImportError:
  import ConfigParser as configparser

from acestream_engine import AcestreamEngine
from acestream_player import AcestreamPlayer


class AcestreamLauncher(object):
  """Acestream Launcher"""

  engine  = None
  player  = None
  exiting = False

  def __init__(self):
    self.atty = sys.stdin.isatty()
    self.opts = self.read_config()

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
      '-e', '--engine',
      help='the engine command to use (default: acestreamengine --client-console)',
      default=self.get_option('engine')
    )
    parser.add_argument(
      '-p', '--player',
      help='the media player command to use (default: mpv)',
      default=self.get_option('player')
    )
    parser.add_argument(
      '-t', '--timeout',
      help='time in seconds to wait for stream playback (default: 30)',
      default=self.get_option('timeout', 'getint')
    )
    parser.add_argument(
      '-v', '--verbose',
      help='show engine and media player output in console',
      action='store_true',
      default=self.get_option('verbose', 'getboolean')
    )

    self.args = parser.parse_args()
    self.stdo = { 'stdout': self.output, 'stderr': self.output }

  @property

  def output(self):
    return None if self.args.verbose else subprocess.PIPE

  @property

  def notifier(self):
    """Check if libnotify is available"""

    if hasattr(self, 'libnotify'):
      return self.libnotify

    try:
      subprocess.call(['notify-send', '-v'], **self.stdo)
      self.libnotify = True
    except OSError:
      self.libnotify = False

    return self.libnotify

  def read_config(self):
    """Read configuration file"""

    config = configparser.RawConfigParser({
      'engine': 'acestreamengine --client-console',
      'player': 'mpv',
      'timeout': '30',
      'verbose': 'False'
    })

    config.add_section('tty')
    config.add_section('browser')
    config.read(os.path.expanduser('~/.config/acestream-launcher/config'))

    return config

  def get_option(self, option, method='get'):
    """Get configuration option"""

    section = 'tty' if self.atty else 'browser'
    return getattr(self.opts, method)(section, option)

  def write(self, message):
    """Write message to stdout"""

    sys.stdout.write("\x1b[2K\r%s" % message)
    sys.stdout.flush()

  def notify(self, message):
    """Show player status notifications"""

    messages = {
      'running':     'Acestream engine running...',
      'noengine':    'Acestream engine not found in provided path!',
      'connecting':  'Connecting to Acestream engine...',
      'noconnect':   'Cannot connect to Acestream engine!',
      'noplayer':    'Media player not found in provided path!',
      'waiting':     'Waiting for stream response...',
      'playing':     'Streaming started, launching player...',
      'unavailable': 'Stream unavailable!'
    }

    message = messages.get(message, None)

    if not message or self.exiting:
      return

    if self.atty:
      self.write(message)

    if not self.atty and self.notifier:
      name = 'Acestream Launcher'
      icon = self.args.player.split()[0]
      args = ['notify-send', '-h', 'int:transient:1', '-i', icon, name, message]

      subprocess.call(args, **self.stdo)

  def stats(self, engine):
    """Print stream statistics"""

    if self.exiting:
      return

    labels = { 'dl': 'playing', 'prebuf': 'buffering' }
    status = labels[engine.status]

    labels = 'down: %.1f kb/s up: %.1f kb/s peers: %d'
    sstats = labels % (engine.speed_down, engine.speed_up, engine.peers)

    if engine.is_live:
      label = 'LIVE - status: %s %s'
      stats = (status, sstats)
    else:
      label = 'VOD - status: %s total: %.2f%% %s'
      stats = (status, engine.total_progress, sstats)

    self.write(label % stats)

  def start_stream(self):
    """Strart streaming"""

    self.engine.open_stream(self.args.url, self.atty, int(self.args.timeout))

  def start_player(self, url):
    """Start media player"""

    self.player = AcestreamPlayer()

    self.player.connect('message', self.notify)
    self.player.connect('error', self.quit)
    self.player.connect('exit', self.quit)

    self.player.start_player(url=url, command=self.args.player, kwargs=self.stdo)

  def run(self):
    """Start acestream and media player"""

    self.engine = AcestreamEngine()

    self.engine.connect('message', self.notify)
    self.engine.connect('stats', self.stats)
    self.engine.connect('error', self.quit)
    self.engine.connect('exit', self.quit)

    self.engine.connect('running', self.start_stream)
    self.engine.connect('playing', self.start_player)

    self.engine.start_engine(command=self.args.engine, kwargs=self.stdo)

  def quit(self):
    """Stop acestream and media player"""

    if not self.exiting:
      self.exiting = True
      print('\n\nExiting...')

    if self.player:
      self.player.stop_player()
      self.player = None

    if self.engine:
      self.engine.close_stream()
      self.engine.stop_engine()
      self.engine = None


if __name__ == '__main__':
  try:
    launcher = AcestreamLauncher()
    launcher.run()
  except KeyboardInterrupt:
    launcher.quit()
