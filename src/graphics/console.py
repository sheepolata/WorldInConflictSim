import math

class Console(object):
    """docstring for Console"""
    def __init__(self, max_lines=20, head="", tail=""):
        super(Console, self).__init__()
        self.lines = []
        self.max = max_lines
        self.line_head = head
        self.line_tail = tail

    def get_lines(self):
        return self.lines

    def log(self, s):
        l = "{}{}{}".format(self.line_head, s, self.line_tail)
        self.lines.append(l)
        if len(self.lines) > self.max:
            self.lines = self.lines[1:]

    def push_back(self, s):
        self.log(s)

    def push_front(self, s):
        l = "{}{}{}".format(self.line_head, s, self.line_tail)
        self.lines.insert(0, l)
        if len(self.lines) > self.max:
            self.lines = self.lines[:-1]

    def clear(self):
        del self.lines[:]

    def print(self):
        for l in self.lines:
            print(l)