#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cairo
import json

from gi.repository import Gdk


FONT = ('Monospace', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
LAYOUT = 'latam'  # es-latam layout
INTRO_KEY = '↲'
DEL_KEY = '←'
TAB_KEY = '⇄'
COLORS = {'background': (0.5, 0.5, 0.5),
          'key-button': (0.7, 0.7, 0.7),
          'key-letter': (1, 1, 1),
          'key-selected': (0.6, 0.6, 0.6)}

MAYUS_KEY = '⇧'
MAYUS_KEYS = {'↾': [0, 'Never'],
              '⇧': [1, 'StartOnly'],
              '⇈': [2, 'Forever']}

SPECIALS_SHIFT = {'<': '>',
                  '{': '[',
                  '}': ']',
                  ',': ';',
                  '.': ':',
                  '-': '_',
                  '1': '!',
                  '2': '@',
                  '3': '#',
                  '4': '$',
                  '5': '%',
                  '6': '^',
                  '7': '&',
                  '8': '*',
                  '9': '(',
                  '0': ')'}


class KeysDict(object):
    def __init__(self):

        self.lowers = []
        self.uppers = []

    def __getitem__(self, name):
        if name in self.lowers:
            number = self.lowers.index(name)
            return self.uppers[number]

        elif name in self.uppers:
            number = self.uppers.index(name)
            return self.lowers[number]

        else:
            raise KeyError(str(name))

    def __setitem__(self, name, value):
        self.lowers.append(name)
        self.uppers.append(value)

    def __delitem__(self, name):
        if name in self.lowers:
            number = self.lowers.index(name)
            self.lowers.remove(number)
            self.uppers.remove(self.lowers[number])

        elif name in self.uppers:
            number = self.uppers.index(name)
            self.uppers.remove(name)
            self.lowers.remove(self.lowers[number])

        else:
            raise KeyError(str(name))

    def __contains__(self, name):
        return name in self.lowers or name in self.uppers

    def __add__(self, _object):
        if type(_object) == dict:
            for key, value in _object.items():
                return self.lowers + [key], self.uppers + [value]

        elif isinstance(_object, KeysDict):
            return self.lowers + _object.lowers, self.uppers + _object.uppers

        else:
            raise TypeError("unsupported operand type(s) for +: %s and %s" % (
                type(self), type(_object)))

    def __mul__(self, _object):
        if type(_object) == int:
            return self.lowers * _object, self.uppers * _object

        else:
            raise TypeError(
                "unsupported operand type(s) for *: 'KEYS1' and '%s'" % str(
                    type(_object)))

    def __len__(self):
        return len(self.lowers)

    def __cmp__(self, _object):
        if not isinstance(_object, KeysDict):
            return False

        else:
            lowers = self.lowers == _object.lowers
            uppers = self.uppers == _object.uppers

            return lowers and uppers

    def __iter__(self):
        for x in self.lowers:
            yield x

    def index(self, value):
        if value in self.lowers:
            return self.lowers.index(value)
        elif value in self.uppers:
            return self.uppers.index(value)


def set_mayus_key(key):
    global MAYUS_KEY
    MAYUS_KEY = key


class KEYS1(KeysDict):

    def __init__(self):
        KeysDict.__init__(self)

        self.lowers = [str(x) for x in range(1, 10)] + ['0', DEL_KEY]
        self.uppers = [
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', DEL_KEY]


class KEYS2(KeysDict):

    def __init__(self):
        KeysDict.__init__(self)

        self.lowers = [u'⇄', 'q', 'w', 'e', 'r', 't', 'y', 'i', 'o', 'p']
        self.uppers = [u'⇄', 'Q', 'W', 'E', 'R', 'T', 'Y', 'I', 'O', 'P']


class KEYS3(KeysDict):

    def __init__(self):
        KeysDict.__init__(self)

        self.lowers = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '{', '}']
        self.uppers = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '[', ']']

        if 'latam' in LAYOUT:
            self.lowers.insert(-2, 'ñ')
            self.uppers.insert(-2, 'Ñ')


class KEYS4(KeysDict):

    def __init__(self):
        KeysDict.__init__(self)

        self.lowers = [
            MAYUS_KEY, '<', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-']
        self.uppers = [
            MAYUS_KEY, '>', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ';', ':', '_']


class KEYS5(KeysDict):

    def __init__(self):
        KeysDict.__init__(self)

        self.lowers = ['SPACE']
        self.uppers = ['SPACE']


def get_in_list(key):
    if key in KEYS1():
        _list = KEYS1()
        n = 1
    elif key in KEYS2():
        _list = KEYS2()
        n = 2
    elif key in KEYS3():
        _list = KEYS3()
        n = 3
    elif key in KEYS4() or key in MAYUS_KEYS:
        _list = KEYS4()
        n = 4
    elif key in KEYS5():
        _list = KEYS5()
        n = 5

    return _list, n


def get_all_keys():
    return KEYS1() + KEYS2() + KEYS3() + KEYS4() + KEYS5()


def get_mayus_key(mayus, text, key):
    shift = False

    if mayus == 'Forever':
        shift = True

    elif mayus == 'Never':
        shift = False

    elif mayus == 'StartOnly':
        shift = key.lower_key not in KEYS1() and (
            text.endswith('\n') or text.strip().endswith('.') or not text)

    _key = key.mayus_key if shift else key.lower_key
    return _key


def gdk_to_cairo(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0)


def cairo_to_gdk(color):
    return Gdk.Color(65535 * color[0], 65535 * color[1], 65535 * color[2])


def get_color(color):
    return tuple(eval(eval(json.dumps(color))))