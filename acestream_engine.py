# -*- coding: utf-8 -*-

"""AceStream Engine: Communicate with the AceStream Engine HTTP API"""

import os
import json
import time
import signal
import hashlib
import threading
import subprocess

try:
  import urllib.request as request
except ImportError:
  import urllib as request


class AcestreamEngine(object):
  """AceStream Engine"""

  _events = []

  def __init__(self, host='127.0.0.1', port='6878'):
    self.host = host
    self.port = port
    self.live = False
    self.poll = True

  @property

  def running(self):
    """Check if AceStream Engine is running"""

    status_url = self.get_url('webui/api/service', method='get_version', format='json')
    req_output = self.request(status_url)
    output_res = req_output.get('result', False)

    return output_res is not False

  def connect(self, event_name, callback_fn):
    """Register event and callback function"""

    self._events.append({ 'event_name': event_name, 'callback_fn': callback_fn })

  def emit(self, event_name, *callback_args):
    """Emit event and execute callback function"""

    for event in self._events:
      if event['event_name'] == event_name:
        event['callback_fn'](*callback_args)

  def timeout(self, timeout, attribute, message):
    """Wait for attribute to become true in given time"""

    while timeout > 0 and not getattr(self, attribute):
      time.sleep(1)
      timeout = timeout - 1

    if timeout == 0:
      self.emit('message', message)
      self.emit('error')

  def request(self, url):
    """Send engine API request"""

    try:
      response = request.urlopen(url)
      return json.loads(response.read())
    except (IOError, ValueError):
      return {}

  def get_url(self, query_path, **params):
    """Get engine API url"""

    query_params = ['%s=%s' % (i, params[i]) for i in params.keys()]
    query_params = '&'.join(query_params)

    return 'http://%s:%s/%s?%s' % (self.host, self.port, query_path, query_params)

  def get_stream_url(self, url):
    """Get engine API stream url"""

    if url.startswith('http'):
      stream_uid = hashlib.sha1(url.encode('utf-8')).hexdigest()
      query_args = { 'url': url }
    else:
      stream_pid = url.split('://')[-1]
      stream_uid = hashlib.sha1(stream_pid.encode('utf-8')).hexdigest()
      query_args = { 'id': stream_pid }

    return self.get_url('ace/getstream', format='json', sid=stream_uid, **query_args)

  def open_request(self, url):
    """Open URL request on engine API"""

    req_output = self.request(self.get_stream_url(url))
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err or not output_res:
      return

    for key in output_res.keys():
      setattr(self, key, output_res[key])

  def close_request(self):
    """Close request on engine API"""

    if hasattr(self, 'command_url'):
      stop_url = self.get_url(self.command_url, method='stop')
      self.request(stop_url)

  def update_stream_stats(self):
    """Update stream statistics"""

    req_output = self.request(self.stat_url)
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err or not output_res:
      return

    self.available = True

    for key in output_res.keys():
      setattr(self, key, output_res[key])

    if self.status == 'check':
      return

    if self.downloaded == 0 and self.speed_down == 0:
      self.status = 'prebuf'

    if not self.live and self.status == 'dl':
      self.live = True
      time.sleep(2)

  def poll_stream_stats(self):
    """Update stream statistics"""

    while self.poll:
      time.sleep(1)
      self.update_stream_stats()
      self.emit('stats', self)

  def poll_stats(self):
    """Run stream stats watcher in thread"""

    thread = threading.Thread(target=self.poll_stream_stats)
    thread.start()

  def run_engine(self, args, kwargs):
    """Start AceStream Engine process"""

    try:
      self.engine = subprocess.Popen(args, preexec_fn=os.setsid, **kwargs)
      self.emit('message', 'running')
      self.emit('running')

      self.engine.communicate()
      delattr(self, 'engine')

      self.emit('message', 'exit')
      self.emit('exit')
    except OSError:
      self.emit('message', 'noengine')
      self.emit('error')

  def start_engine(self, command='acestreamengine --client-console', kwargs={}):
    """Start AceStream Engine"""

    if self.running:
      self.emit('message', 'running')
      self.emit('running')
    else:
      cmargs = command.split()
      thread = threading.Thread(target=self.run_engine, args=[cmargs, kwargs])

      thread.start()

  def stop_engine(self):
    """Stop AceStream Engine"""

    if hasattr(self, 'engine'):
      os.killpg(os.getpgid(self.engine.pid), signal.SIGTERM)

  def open_stream(self, url, emit_stats=False, timeout=30):
    """Open AceStream URL"""

    self.emit('message', 'connecting')
    self.timeout(timeout, 'running', 'noconnect')

    self.emit('message', 'waiting')
    self.open_request(url)

    if not hasattr(self, 'playback_url'):
      self.emit('message', 'unavailable')
      self.emit('error')

    self.available = False
    self.poll_stats()

    self.poll = emit_stats
    self.timeout(timeout, 'available', 'unavailable')

    self.emit('message', 'playing')
    self.emit('playing', self.playback_url)

  def close_stream(self):
    """Close current stream"""

    self.poll = False
    self.close_request()
