import threading

class DSTimer:
    def __init__(self, interval, elapsedHander):
        self._interval = interval
        self._elapsedHander = elapsedHander
        self.init() 

    def init(self):
        self.Timer = threading.Timer(self._interval, self._elapsedHander)

    def Start(self):
        self.Timer.start()

    def Cancel(self):
        self.Timer.cancel()

    def Restart(self):
        self.Cancel()
        self.init()
        self.Start()
