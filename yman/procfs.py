import os


class Process(object):
    """Process object that allows easy retrieval of process information"""

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self._env = None

        if not os.path.exists(f'/proc/{self.pid}'):
            raise Exception('Process no longer exists')

    @staticmethod
    def _decode_null_strs(data):
        return [el.decode() for el in data.split(b'\x00')][:-1]

    @property
    def cmdline(self) -> list[str]:
        """Returns the command line arguments for the process"""
        f = open(f'/proc/{self.pid}/cmdline', 'rb')
        data = f.read()
        f.close()
        return self._decode_null_strs(data)

    @property
    def env(self) -> dict[str, str]:
        """Returns the environment for a given process"""
        if not self._env:
            f = open(f'/proc/{self.pid}/environ', 'rb')
            data = f.read()
            f.close()
            self._env = dict([el.split('=', 1) for el in self._decode_null_strs(data)])
        return self._env

    @property
    def cwd(self):
        return self.env['PWD']
