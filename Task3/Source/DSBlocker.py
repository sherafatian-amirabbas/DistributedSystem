from DSTimer import DSTimer

class DSBlocker:
    def __init__(self, releaseHander):
        self.releaseHander = releaseHander
        self.timeout = -1

        self.timer = DSTimer(1, self.timer_elapsed)
        self.initialize()

    def Block(self, timeout):
        if timeout > 0:
            self.timeout = timeout
        return self.block() # blocks the current thread until the condition is satisfied via the releaseHander

    # ---------------------------------------------------------------------------------------- handlers

    def timer_elapsed(self):

        if self.timeout > 0:
            self.timeout -= 1

        self.timer.Restart()

    # ------------------------------ private methods

    def initialize(self):
        self.timer.Start()

    def block(self):
        while True:
            if (self.releaseHander != None and self.releaseHander() == True):
                self.timeout = -1
                return 0
            elif self.timeout == 0:
                self.timeout = -1
                return 1