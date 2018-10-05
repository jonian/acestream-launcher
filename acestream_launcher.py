#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Acestream Launcher: Open acestream links with any media player"""

import os
import sys
import signal
import argparse
import subprocess

try:
  import configparser
except ImportError:
  import ConfigParser as configparser

from acestream_engine import AcestreamEngine


class AcestreamLauncher(object):
  """Acestream Launcher"""

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

  def notify(self, message, terminate=False):
    """Show player status notifications"""

    messages = {
      'running': 'Acestream engine running...',
      'noengine': 'Acestream engine not found in provided path!',
      'connecting': 'Connecting to Acestream engine...',
      'noconnect': 'Cannot connect to Acestream engine!',
      'noplayer': 'Media player not found in provided path!',
      'waiting': 'Waiting for stream response...',
      'started': 'Streaming started, launching player...',
      'unavailable': 'Stream unavailable!'
    }

    message = messages[message]

    if self.atty:
      self.write(message)

    if not self.atty and self.notifier:
      name = 'Acestream Launcher'
      icon = self.args.player.split()[0]
      args = ['notify-send', '-h', 'int:transient:1', '-i', icon, name, message]

      subprocess.call(args, **self.stdo)

    if terminate:
      self.quit()

  def stats(self):
    """Print stream statistics"""

    labels = { 'dl': 'playing', 'prebuf': 'buffering' }
    status = labels[self.engine.status]

    labels = 'down: %.1f kb/s up: %.1f kb/s peers: %d'
    sstats = labels % (self.engine.speed_down, self.engine.speed_up, self.engine.peers)

    if self.engine.is_live:
      label = 'LIVE - status: %s %s'
      stats = (status, sstats)
    else:
      label = 'VOD - status: %s total: %.2f%% %s'
      stats = (status, self.engine.total_progress, sstats)

    self.write(label % stats)

  def start_stream(self):
    """Strart streaming"""

    self.engine = AcestreamEngine(output=self.output)

    self.engine.connect('message', self.notify)
    self.engine.connect('stats', self.stats)
    self.engine.connect('error', self.quit)

    self.engine.start_engine(self.args.engine.split())
    self.engine.open_stream(self.args.url, self.atty)

  def start_player(self):
    """Start media player"""

    player_args = self.args.player.split()
    player_args.append(self.engine.playback_url)

    try:
      self.player = subprocess.Popen(player_args, preexec_fn=os.setsid, **self.stdo)
      self.player.communicate()
    except OSError:
      self.notify('noplayer', True)

  def run(self):
    """Start acestream and media player"""

    self.start_stream()
    self.start_player()
    self.quit()

  def quit(self, abort=False):
    """Stop acestream and media player"""

    self.engine.close_stream()
    self.engine.stop_engine()

    if abort and hasattr(self, 'player'):
      os.killpg(os.getpgid(self.player.pid), signal.SIGTERM)

    print('\n\nExiting...')
    sys.exit()


if __name__ == '__main__':
  try:
    launcher = AcestreamLauncher()
    launcher.run()
  except KeyboardInterrupt:
    launcher.quit(True)
