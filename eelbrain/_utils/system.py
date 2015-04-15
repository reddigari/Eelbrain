# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from distutils.version import LooseVersion
from subprocess import Popen
import platform


class Caffeinator(object):
    """Keep track of processes blocking idle sleep"""

    def __init__(self):
        self._popen = None
        self.n_processes = 0
        if platform.system() == 'Darwin':
            x_version = LooseVersion(platform.mac_ver()[0])
            if x_version >= LooseVersion('10.8'):
                self.enabled = True
                return
        self.enabled = False

    def __enter__(self):
        if self.n_processes == 0 and self.enabled:
            self._popen = Popen('caffeinate')
        self.n_processes += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.n_processes -= 1
        if self.n_processes == 0 and self.enabled:
            self._popen.terminate()


caffeine = Caffeinator()
