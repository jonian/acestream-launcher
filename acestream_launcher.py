#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Acestream Launcher: Open acestream links with any media player"""

import os
import sys
import json
import time
import signal
import shutil
import hashlib
import argparse
import threading
import subprocess

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
      '-e', '--engine',
      help='the engine command to use (default: acestreamengine --client-console)',
      default='acestreamengine --client-console'
    )
    parser.add_argument(
      '-p', '--player',
      help='the media player command to use (default: mpv)',
      default='mpv'
    )

    self.atty = sys.stdin.isatty()
    self.args = parser.parse_args()
    self.live = False
    self.poll = True
    self.stdo = { 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE }

  @property

  def notifier(self):
    """Check if libnotify is available"""

    if not hasattr(self, 'libnotify'):
      self.libnotify = shutil.which('notify-send') is None

    return self.libnotify

  @property

  def running(self):
    """Check if acestream engine is running"""

    status_url = self.get_url('webui/api/service', method='get_version', format='json')
    req_output = self.request(status_url)
    output_res = req_output.get('result', False)

    return output_res is not False

  def write(self, message):
    """Write message to stdout"""

    sys.stdout.write("\x1b[2K\r%s" % message)
    sys.stdout.flush()

  def notify(self, message, terminate=False):
    """Show player status notifications"""

    messages = {
      'running': 'Acestream engine running...',
      'noengine': 'Acestream engine not found in provided path!',
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

  def get_url(self, query_path, **params):
    """Get engine API url"""

    query_params = ['%s=%s' % (i, params[i]) for i in params.keys()]
    query_params = '&'.join(query_params)

    return 'http://127.0.0.1:6878/%s?%s' % (query_path, query_params)

  def request(self, url):
    """Send engine API request"""

    curl_proccess = subprocess.Popen(['curl', '-s', url], **self.stdo)
    output, error = curl_proccess.communicate()

    try:
      return json.loads(output)
    except ValueError:
      return {}

  def get_stream_url(self):
    """Get engine API stream url"""

    if self.args.url.startswith('http'):
      stream_uid = hashlib.sha1(self.args.url.encode('utf-8')).hexdigest()
      query_args = { 'url': self.args.url }
    else:
      stream_pid = self.args.url.split('://')[-1]
      stream_uid = hashlib.sha1(stream_pid.encode('utf-8')).hexdigest()
      query_args = { 'id': stream_pid }

    return self.get_url('ace/getstream', format='json', sid=stream_uid, **query_args)

  def get_stream_stats(self):
    """Get stream statistics"""

    if not self.poll:
      return

    req_output = self.request(self.stat_url)
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err:
      return

    for key in output_res.keys():
      setattr(self, key, output_res[key])

    if self.status == 'check':
      return

    if not self.live and self.status == 'dl':
      self.live = True
      self.poll = self.atty

      time.sleep(2)

    if self.atty:
      self.write_stream_stats()

  def write_stream_stats(self):
    """Print stream statistics"""

    labels = { 'dl': 'playing', 'prebuf': 'buffering' }
    status = labels[self.status]

    labels = 'down: %.1f kb/s up: %.1f kb/s peers: %d'
    sstats = labels % (self.speed_down, self.speed_up, self.peers)

    if self.is_live:
      label = 'LIVE - status: %s %s'
      stats = (status, sstats)
    else:
      label = 'VOD - status: %s total: %.2f%% %s'
      stats = (status, self.total_progress, sstats)

    self.write(label % stats)

  def watch_stream_stats(self):
    """Update stream statistics"""

    while self.poll:
      time.sleep(1)
      self.get_stream_stats()

  def watch_stream(self):
    """Run stream watcher in thread"""

    thread = threading.Thread(target=self.watch_stream_stats)
    thread.start()

  def start_engine(self):
    """Start acestream engine"""

    if self.running:
      return

    try:
      engine_args = self.args.engine.split()
      self.engine = subprocess.Popen(engine_args, preexec_fn=os.setsid, **self.stdo)

      while not self.running:
        time.sleep(1)

      self.notify('running')
    except OSError:
      self.notify('noengine', True)

  def start_stream(self):
    """Strart streaming"""

    req_output = self.request(self.get_stream_url())
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err or not output_res:
      self.notify('unavailable', True)

    for key in output_res.keys():
      setattr(self, key, output_res[key])

    self.notify('waiting')
    self.watch_stream()

    while not self.live:
      time.sleep(1)

    self.notify('started')

  def start_player(self):
    """Start media player"""

    player_args = self.args.player.split()
    player_args.append(self.playback_url)

    try:
      self.player = subprocess.Popen(player_args, **self.stdo)
      self.player.communicate()
    except OSError:
      self.notify('noplayer', True)

  def run(self):
    """Start acestream and media player"""

    try:
      self.start_engine()
      self.start_stream()
      self.start_player()
    except KeyboardInterrupt:
      self.poll = False

    self.quit()

  def quit(self):
    """Stop acestream and media player"""

    self.poll = False

    if hasattr(self, 'command_url'):
      stop_url = self.get_url(self.command_url, method='stop')
      self.request(stop_url)

    if hasattr(self, 'engine'):
      os.killpg(os.getpgid(self.engine.pid), signal.SIGTERM)

    print('\n\nExiting...')
    sys.exit()


if __name__ == '__main__':
  launcher = AcestreamLauncher()
  launcher.run()
