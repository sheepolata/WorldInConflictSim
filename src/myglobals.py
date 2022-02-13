import sys

sys.path.append('./GraphEngine')

import math

import console


class myDatetime(object):
    def __init__(self, simu_day):
        self.simu_day = simu_day

        self.day = ((self.simu_day % 365) % 30) + 1
        self.month = (((self.simu_day % 365) // 30) % 12) + 1
        self.year = (self.simu_day // 365) + 1


class LogConsole(console.Console):

    def __init__(self, max_lines=20):
        super(LogConsole, self).__init__(max_lines=max_lines)

    def get_date_to_string(day):
        _year = math.floor(day / (12 * 28))
        _month = (math.floor(day / 28)) % 12
        _day = day % 28
        d = myDatetime(day)
        h = "{:02d}/{:02d}/{:04d}".format(d.day, d.month, d.year)
        return h

    def set_head(self, day):
        self.line_head = "{} - ".format(LogConsole.get_date_to_string(day))

    def log(self, s, day):
        self.set_head(day)
        super(LogConsole, self).log(s)

    def push_back(self, s, day):
        self.log(s, day)

    def push_front(self, s, day):
        self.set_head(day)
        super(LogConsole, self).push_front(s)


InfoConsole = console.Console(max_lines=1000)
LogConsoleInst = LogConsole(max_lines=18)
