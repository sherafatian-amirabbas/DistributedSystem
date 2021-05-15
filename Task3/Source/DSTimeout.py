from DSTimer import DSTimer

class DSTimeout:
    def __init__(self, timeout):
        self.timeout = timeout
        self.handler = None
        self.timer = DSTimer(1, self.timer_elapsed)
        self.passedSeconds = 0

    def Reset(self):
        self.Restart()

    def Run(self, handler):
        self.handler = handler
        self.timer.Start()

    def timer_elapsed(self):
        self.passedSeconds = self.passedSeconds + 1
        if self.passedSeconds == self.timeout:
            self.timer.Cancel()
            self.handler()
        else: 
            self.timer.Restart()
