import sys
import subprocess


class NotifyHandler(object):

  def __init__(self, player):
    self.player = player
    self.isatty = sys.stdin.isatty()
    self.notify = self._notify_send(['-v'])

  def print_message(self, message):
    if message and self.isatty:
      sys.stdout.write("\x1b[2K\r%s" % message)
      sys.stdout.flush()

  def send_message(self, message):
    if message and self.notify and not self.isatty:
      name = 'Acestream Launcher'
      icon = self.player.split()[0]
      args = ['-h', 'int:transient:1', '-i', icon, name, message]

      self._notify_send(args)

  def print_stats(self, stream, stats):
    labels = { 'dl': 'playing', 'prebuf': 'buffering' }
    status = labels[stream.status]

    labels = 'down: %.1f kb/s up: %.1f kb/s peers: %d'
    sstats = labels % (stats.speed_down, stats.speed_up, stats.peers)

    if stream.is_live:
      label = 'LIVE - status: %s %s'
      stats = (status, sstats)
    else:
      label = 'VOD - status: %s total: %.2f%% %s'
      stats = (status, stats.total_progress, sstats)

    self.print_message(label % stats)

  def _notify_send(self, args):
    try:
      command = ['notify-send'] + args
      subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      return True
    except OSError:
      return False
