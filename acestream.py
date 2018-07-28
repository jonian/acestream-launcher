# -*- coding: utf-8 -*-

"""Acestream Engine: Communicate with the Acestream Engine HTTP API"""

import os
import json
import time
import signal
import hashlib
import threading
import subprocess

class Acestream(object):
  """Acestream Engine"""

  _events = []

  def __init__(self):
    self.live = False
    self.poll = False
    self.stdo = { 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE }

  @property

  def running(self):
    """Check if acestream engine is running"""

    status_url = self.get_url('webui/api/service', method='get_version', format='json')
    req_output = self.request(status_url)
    output_res = req_output.get('result', False)

    return output_res is not False

  def connect(self, event_name, callback_fn):
    self._events.append({ 'event_name': event_name, 'callback_fn': callback_fn })

  def emit(self, event_name, *callback_args):
    for event in self._events:
      if event['event_name'] == event_name:
        event['callback_fn'](*callback_args)

  def request(self, url):
    """Send engine API request"""

    curl_proccess = subprocess.Popen(['curl', '-s', url], **self.stdo)
    output, error = curl_proccess.communicate()

    try:
      return json.loads(output)
    except ValueError:
      return {}

  def get_url(self, query_path, **params):
    """Get engine API url"""

    query_params = ['%s=%s' % (i, params[i]) for i in params.keys()]
    query_params = '&'.join(query_params)

    return 'http://127.0.0.1:6878/%s?%s' % (query_path, query_params)

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

    if not self.live and self.status == 'dl':
      self.live = True

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
    """Start acestream engine"""

    if self.running:
      return

    try:
      engine_args = args if args else ['acestreamengine', '--client-console']
      self.engine = subprocess.Popen(engine_args, preexec_fn=os.setsid, **self.stdo)

      while not self.running:
        time.sleep(1)

      self.emit('message', 'running')
    except OSError:
      self.emit('error', 'noengine', True)

  def stop_engine(self):
    """Stop acestream engine"""

    if hasattr(self, 'engine'):
      os.killpg(os.getpgid(self.engine.pid), signal.SIGTERM)

  def open_stream(self, url, emit_stats=False):
    """Open acestream url"""

    req_output = self.request(self.get_stream_url(url))
    output_res = req_output.get('response', False)
    output_err = req_output.get('error', False)

    if output_err or not output_res:
      self.emit('error', 'unavailable', True)

    for key in output_res.keys():
      setattr(self, key, output_res[key])

    self.emit('message', 'waiting')

    if emit_stats:
      self.poll = True
      self.poll_stats()

    while not self.live:
      time.sleep(1)

    self.emit('message', 'started')

  def close_stream(self):
    """Close current stream"""

    self.poll = False

    if hasattr(self, 'command_url'):
      stop_url = self.get_url(self.command_url, method='stop')
      self.request(stop_url)
