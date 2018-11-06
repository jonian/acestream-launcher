# -*- coding: utf-8 -*-

"""AceStream Player: Play stream URL with external media player"""

import os
import signal
import threading
import subprocess


class AcestreamPlayer(object):
  """AceStream Player"""

  _events = []

  def connect(self, event_name, callback_fn):
    """Register event and callback function"""

    self._events.append({ 'event_name': event_name, 'callback_fn': callback_fn })

  def emit(self, event_name, *callback_args):
    """Emit event and execute callback function"""

    for event in self._events:
      if event['event_name'] == event_name:
        event['callback_fn'](*callback_args)

  def run_player(self, args, options):
    """Start media player process"""

    try:
      self.player = subprocess.Popen(args, **options)
      self.emit('message', 'running')
      self.emit('running')

      self.player.communicate()
      delattr(self, 'player')

      self.emit('message', 'exit')
      self.emit('exit')
    except OSError:
      self.emit('message', 'noplayer')
      self.emit('error')

  def start_player(self, args=None, output=subprocess.PIPE):
    """Start media player"""

    args = args if args else ['mpv']
    opts = { 'preexec_fn': os.setsid, 'stdout': output, 'stderr': output }

    thread = threading.Thread(target=self.run_player, args=[args, opts])
    thread.start()

  def stop_player(self):
    """Stop media player"""

    if hasattr(self, 'player'):
      os.killpg(os.getpgid(self.player.pid), signal.SIGTERM)
