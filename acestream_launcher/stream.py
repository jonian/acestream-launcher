import time

from acestream.object import Observable
from acestream.server import Server
from acestream.engine import Engine
from acestream.stream import Stream


class StreamHandler(Observable):

  def __init__(self, bin, host='127.0.0.1', port=6878, timeout=30):
    Observable.__init__(self)

    self.stream    = None
    self.params    = None
    self.playing   = False
    self.available = False
    self.timeout   = int(timeout)
    self.server    = Server(host=host, port=port)
    self.engine    = Engine(bin=bin)

  def start(self, param, **kwargs):
    self.params = self._parse_stream_param(param)

    self.emit('notify', 'Connecting to Acestream engine...')
    self._start_engine(**kwargs)

  def stop(self):
    self.engine.stop()

  def _start_engine(self, **kwargs):
    if not self.server.available:
      self.engine.connect('started', self._on_engine_started)
      self.engine.connect('terminated', self._on_engine_terminated)
      self.engine.connect('error', self._on_engine_error)

      self.engine.start(daemon=True, **kwargs)
    else:
      self._on_engine_started()

  def _start_stream(self):
    self.stream = Stream(self.server, **self.params)

    self.stream.connect('status::changed', self._on_stream_status_changed)
    self.stream.connect('stats::updated', self._on_stream_stats_updated)
    self.stream.connect('error', self._on_stream_error)

    self.stream.start()

  def _parse_stream_param(self, param):
    if param.startswith('http'):
      return { 'url': param }
    else:
      return { 'id': param.split('://')[-1] }

  def _timeout(self, object, attribute, message):
    while self.timeout > 0 and not getattr(object, attribute):
      self.timeout = self.timeout - 1
      time.sleep(1)

    if self.timeout == 0:
      self.emit('notify', message)
      self.emit('error')

  def _on_engine_started(self):
    self._timeout(self.server, 'available', 'Cannot connect to Acestream engine!')
    self.emit('notify', 'Waiting for stream response...')

    self._start_stream()
    self._timeout(self, 'available', 'Stream unavailable!')

  def _on_engine_terminated(self):
    self.emit('terminated')

  def _on_engine_error(self, _message=None):
    self.emit('notify', 'Acestream engine not found in provided path!')
    self.emit('error')

  def _on_stream_status_changed(self):
    if self.stream.status and not self.available:
      self.available = True

    if self.stream.status == 'dl' and not self.playing:
      self.playing = True

      self.emit('notify', 'Streaming started, launching player...')
      self.emit('playing', self.stream.playback_url)

  def _on_stream_stats_updated(self):
    self.emit('stats::updated', self.stream, self.stream.stats)

  def _on_stream_error(self, _message=None):
    self.emit('notify', 'Stream unavailable!')
    self.emit('error')
