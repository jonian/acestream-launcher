import os
import sys

try:
  import configparser
except ImportError:
  import ConfigParser as configparser


class ConfigHandler(object):

  def __init__(self):
    self.isatty = sys.stdin.isatty()
    self.config = configparser.RawConfigParser({
      'engine':  'acestreamengine --client-console',
      'player':  'mpv',
      'timeout': '30',
      'verbose': 'False'
    })

    self._read_config()

  def get(self, option):
    return self._getoption(option, 'get')

  def getint(self, option):
    return self._getoption(option, 'getint')

  def getboolean(self, option):
    return self._getoption(option, 'getboolean')

  def _getoption(self, option, method):
    section = 'tty' if self.isatty else 'browser'
    return getattr(self.config, method)(section, option)

  def _read_config(self):
    self.config.add_section('tty')
    self.config.add_section('browser')
    self.config.read(os.path.expanduser('~/.config/acestream-launcher/config'))
