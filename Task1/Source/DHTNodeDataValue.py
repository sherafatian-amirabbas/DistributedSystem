
# will hold the data of nodes
class DHTNodeDataValue():
    def __init__(self, value):
        self.Value = value

    def ToString(self):
        return '%s' % (self.Value)