import threading
import math
import numpy as np
import time
import pygame

import parameters as params


def get_sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def normalise(a, mini=0, maxi=1):
    denom = float(maxi) - float(mini)
    if denom == 0:
        return 0
    return (float(a) - float(mini)) / denom


def normalise_list(l):
    if len(l) == 1:
        return [normalise(x) for x in l]
    else:
        _min = np.min(l)
        _max = np.max(l)

        return [normalise(x, _min, _max) for x in l]


def normalise_list2(l, mini, maxi):
    return [normalise(x, mini=mini, maxi=maxi) for x in l]


def close_enough(a, b, _thresh=10):
    return abs(a - b) <= _thresh


def distance2p(a, b):
    a0 = float(a[0])
    a1 = float(a[1])
    b0 = float(b[0])
    b1 = float(b[1])
    return math.sqrt((a0 - b0) ** 2 + (a1 - b1) ** 2)


class perpetualTimer():
    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def clamp(x, a, b):
    return max(a, min(x, b))


# return x between _min (include) and _max (exclude)
def between(x, _min, _max):
    return x >= _min and x < _max


# Return [0...1], 1 for max sim, 0 for min
def vector_similarity(v1, v2):
    if len(v1) != len(v2):
        print("ERROR: v1 and v1 sizes are differents")
        return -2

    diffs = []
    for i in range(len(v1)):
        _v1 = v1[i]
        _v2 = v2[i]
        diff = 1 - abs(_v1 - _v2)
        diffs.append(diff)

    return np.mean(diffs)


# Direction in degree
def point_from_direction(point, distance, direction, as_int=False):
    x1 = point[0] + distance * math.cos(direction)
    y1 = point[1] + distance * math.sin(direction)
    if as_int:
        return int(x1), int(y1)
    else:
        return x1, y1


def angle_from_points(p1, p2):
    angle = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    return angle


def random_angle_in_direction(_dir, span):
    a = (_dir - span) % 360
    b = (_dir + span) % 360
    if a > b:
        return math.floor(b + math.floor(params.rng.random() * (b - a)))  # (b, a)
    else:
        return math.floor(a + math.floor(params.rng.random() * (a - b)))  # (a, b)


def random_range(_min, _max):
    _rnd = _min + params.rng.random() * (_max - _min)
    return _rnd


def flatten(l):
    flat_list = [item for sublist in l for item in sublist]
    return flat_list


class LoopingThread(threading.Thread):
    """docstring for LoopingThread"""

    def __init__(self, target=None, freq=200):
        super(LoopingThread, self).__init__()
        self.target = target
        self.freq = freq
        self._stop = False

    def run(self):
        if self.target == None:
            self.join()
            return

        while not self._stop:
            self.target()
            time.sleep(self.freq / 1000.0)

    def stop(self):
        self._stop = True


def flatten(seq):
    for el in seq:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el


def colorize(image, newColor, toone=False):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    _image = image.copy()

    _newColor = (newColor[0], newColor[1], newColor[2], 255)

    if toone:
        # zero out RGB values
        _image.fill((255, 255, 255, 255), None, pygame.BLEND_RGB_ADD)

    # add in new RGB values
    if len(newColor) == 3:
        _image.fill(_newColor[0:3] + (0,), None, pygame.BLEND_RGB_MULT)
    elif len(newColor) == 4:
        _image.fill(_newColor, None, pygame.BLEND_RGB_MULT)

    return _image
