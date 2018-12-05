import time
import argparse
import subprocess

from acestream_launcher.config import ConfigHandler
from acestream_launcher.notify import NotifyHandler

from acestream_launcher.stream import StreamHandler
from acestream_launcher.player import PlayerHandler


class StreamLauncher(object):

  stream  = None
  player  = None
  exiting = False

  def __init__(self):
    config = ConfigHandler()

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
      default=config.get('engine')
    )
    parser.add_argument(
      '-p', '--player',
      help='the media player command to use (default: mpv)',
      default=config.get('player')
    )
    parser.add_argument(
      '-t', '--timeout',
      help='time in seconds to wait for stream playback (default: 30)',
      default=config.getint('timeout')
    )
    parser.add_argument(
      '-v', '--verbose',
      help='show engine and media player output in console',
      action='store_true',
      default=config.getboolean('verbose')
    )

    self.args = parser.parse_args()
    self.noty = NotifyHandler(self.args.player)

  @property
  def output(self):
    output = None if self.args.verbose else subprocess.PIPE
    return { 'stdout': output, 'stderr': output }

  def notify(self, message):
    if message and not self.exiting:
      self.noty.print_message(message)
      self.noty.send_message(message)

  def stats(self, stream, stats):
    if not self.exiting:
      self.noty.print_stats(stream, stats)

  def play(self, url):
    self.player = PlayerHandler(bin=self.args.player)

    self.player.connect('notify', self.notify)
    self.player.connect('error', self.quit)
    self.player.connect('terminated', self.quit)

    self.player.start(url=url, **self.output)

  def run(self):
    self.stream = StreamHandler(bin=self.args.engine, timeout=self.args.timeout)

    self.stream.connect('notify', self.notify)
    self.stream.connect('stats::updated', self.stats)
    self.stream.connect('playing', self.play)
    self.stream.connect('error', self.quit)
    self.stream.connect('terminated', self.quit)

    self.stream.start(param=self.args.url, **self.output)

    while self.stream or self.player:
      time.sleep(1)

  def quit(self):
    if not self.exiting:
      self.exiting = True
      print('\n\nExiting...')

    if self.stream:
      self.stream.stop()
      self.stream = None

    if self.player:
      self.player.stop()
      self.player = None


def main():
  try:
    launcher = StreamLauncher()
    launcher.run()
  except KeyboardInterrupt:
    launcher.quit()


if __name__ == '__main__':
  main()
