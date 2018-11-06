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

  def __init__(self, host='127.0.0.1', port='6878', output=subprocess.PIPE):
    self.host = host
    self.port = port
    self.live = False
    self.poll = True
    self.stdo = { 'stdout': output, 'stderr': output }

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

  def update_stream_stats(self):
    """Update stream statistics"""

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

    if self.downloaded == 0 and self.speed_down == 0:
      self.status = 'prebuf'

    if not self.live and self.status == 'dl':
      self.live = True
      time.sleep(2)

    self.emit('stats')

  def poll_stream_stats(self):
    """Update stream statistics"""

    while self.poll:
      time.sleep(1)
      self.update_stream_stats()

  def poll_stats(self):
    """Run stream stats watcher in thread"""

    thread = threading.Thread(target=self.poll_stream_stats)
    thread.start()

  def start_engine(self, args=None):
    """Start AceStream Engine"""

    if self.running:
      return

    try:
      engine_args = args if args else ['acestreamengine', '--client-console']
      self.engine = subprocess.Popen(engine_args, preexec_fn=os.setsid, **self.stdo)

      self.emit('message', 'running')
      self.emit('running')
    except OSError:
      self.emit('message', 'noengine')
      self.emit('error')

  def stop_engine(self):
    """Stop AceStream Engine"""

    if hasattr(self, 'engine'):
      os.killpg(os.getpgid(self.engine.pid), signal.SIGTERM)

  def open_stream(self, url, emit_stats=False, timeout=10):
    """Open AceStream URL"""

    self.emit('message', 'connecting')

    while timeout > 0 and not self.running:
      time.sleep(1)
      timeout = timeout - 1

    if timeout == 0:
      self.emit('message', 'noconnect')
      self.emit('error')

    req_output = self.request(self.get_stream_url(url))
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err or not output_res:
      self.emit('message', 'unavailable')
      self.emit('error')

    for key in output_res.keys():
      setattr(self, key, output_res[key])

    self.emit('message', 'waiting')
    self.poll_stats()

    while not self.live:
      time.sleep(1)

    self.poll = emit_stats

    self.emit('message', 'playing')
    self.emit('playing')

  def close_stream(self):
    """Close current stream"""

    self.poll = False

    if hasattr(self, 'command_url'):
      stop_url = self.get_url(self.command_url, method='stop')
      self.request(stop_url)
