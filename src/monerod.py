import threading
import subprocess
from src.interfaces.notifier import Notifier
from src.interfaces.observer import Observer
from config import daemon_executable, stagenet
import logging
import logging.config
from src.logging import config as logging_config

class Monerod(Notifier):
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls(stagenet=stagenet())
        return cls._instance

    def __init__(self, stagenet=False):
        self.stagenet = stagenet
        self.process = None
        self._observers = []
        self._ready = False
        self.status_message = ''
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)

    def start(self):
        cmd = f'stdbuf -oL {daemon_executable()}'
        if self.stagenet:
            cmd += ' --stagenet'
        self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def attach(self, observer: Observer):
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def kill(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired: # pragma: no cover
            self.logger.debug('Process did not terminate in time, forcing kill. Wallet may be corrupted.')
            self.process.kill()
            self.process.wait()

    def ready(self):
        while not self._ready:
            output = self.process.stdout.readline()
            self.status_message = output
            if output == 'You are now synchronized with the network. You may now start monero-wallet-cli.':
                self._ready = True
                self.status_message = 'Monero Daemon Ready'
            self.notify()
        return self._ready

    def check_readiness(self): #pragma: no cover
        self.logger.debug('Checking if Monerod Ready')
        threading.Thread(target=self.ready).start()