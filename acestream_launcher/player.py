import os
import signal
import subprocess

from threading import Thread
from acestream.object import Observable


class PlayerHandler(Observable):

  def __init__(self, bin='mpv'):
    Observable.__init__(self)

    self.args    = bin.split()
    self.process = None

  def start(self, url, **kwargs):
    cmargs = self.args
    cmargs.append(url)

    thread = Thread(target=self._start_process, args=(cmargs), kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

  def stop(self):
    if bool(self.process):
      os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

      self.process = None
      self.emit('terminated')

  def _start_process(self, *args, **kwargs):
    try:
      self.process = subprocess.Popen(args, preexec_fn=os.setsid, **kwargs)
      self.emit('started')
      self.process.communicate()

      self.process = None
      self.emit('terminated')
    except OSError:
      self.process = None
      self.emit('notify', 'Media player not found in provided path!')
      self.emit('error')
