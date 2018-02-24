#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Acestream Launcher: Open acestream links with any media player"""

import os
import sys
import json
import time
import signal
import argparse
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

    self.name = 'Acestream Launcher'
    self.args = parser.parse_args()
    self.icon = self.args.player.split()[0]

  @property

  def notifier(self):
    """Check if libnotify is available"""

    if hasattr(self, 'libnotify'):
      return self.libnotify

    try:
      subprocess.run(['notify-send', '-v'], stdout=subprocess.PIPE)
      self.libnotify = True
    except OSError:
      self.libnotify = False

    return self.libnotify

  @property

  def running(self):
    """Check if acestream engine id running"""

    status_url = self.get_url('webui/api/service', method='get_version', format='json')
    req_output = self.request(status_url)
    output_res = req_output.get('result', False)

    return output_res is not False

  def notify(self, message, terminate=False):
    """Show player status notifications"""

    messages = {
      'running': 'Acestream engine running...',
      'started': 'Streaming started, launching player...',
      'noengine': 'Acestream engine not found in provided path!',
      'noplayer': 'Media player not found in provided path!',
      'unavailable': 'Stream unavailable!'
    }

    message = messages[message]
    sys.stdout.write("\r%s" % message)
    sys.stdout.flush()

    if self.notifier:
      args = ['-h', 'int:transient:1', '-i', self.icon, self.name, message]
      subprocess.run(['notify-send', *args], stdout=subprocess.PIPE)

    if terminate:
      self.quit()

  def get_url(self, query_path, **params):
    """Get engine API url"""

    query_params = ['%s=%s' % (i, params[i]) for i in params.keys()]
    query_params = '&'.join(query_params)

    return 'http://127.0.0.1:6878/%s?%s' % (query_path, query_params)

  def request(self, url):
    """Send engine API request"""

    curl_proccess = subprocess.Popen(['curl', '-s', url], stdout=subprocess.PIPE)
    output, error = curl_proccess.communicate()

    try:
      return json.loads(output)
    except json.decoder.JSONDecodeError:
      return {}

  def get_stream_url(self):
    """Get engine API stream url"""

    if self.args.url.startswith('http'):
      query_args = { 'url': self.args.url }
    else:
      query_args = { 'id': self.args.url.split('://')[-1] }

    return self.get_url('ace/getstream', format='json', **query_args)

  def start_engine(self):
    """Start acestream engine"""

    if self.running:
      return

    try:
      engine_args = self.args.engine.split()
      self.engine = subprocess.Popen(engine_args, stdout=subprocess.PIPE)

      self.notify('running')
      time.sleep(2)
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

    self.notify('started')

  def start_player(self):
    """Start media player"""

    player_args = self.args.player.split()
    player_args.append(self.playback_url)

    try:
      self.player = subprocess.Popen(player_args, stdout=subprocess.PIPE)
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
      pass

    self.quit()

  def quit(self):
    """Stop acestream and media player"""

    if hasattr(self, 'command_url'):
      stop_url = self.get_url(self.command_url, method='stop')
      self.request(stop_url)

    if hasattr(self, 'engine'):
      print('\n\nAcestream engine stopping...')
      os.killpg(os.getpgid(self.engine.pid), signal.SIGTERM)

    print('\n\nTerminated')
    sys.exit()


if __name__ == '__main__':
  launcher = AcestreamLauncher()
  launcher.run()
