#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

INCREMENTO = 2
FONT = ('Monospace', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
KEYS1 = [str(x) for x in range(1, 10)] + ['0', '←']
KEYS2 = ['⇄', 'q', 'w', 'e', 'r', 't', 'y', 'i', 'o', 'p']
KEYS3 = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l' ,'ñ', '{', '}']
KEYS4 = ['⇧', '<', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-', '⇧']
KEYS5 = ['Ctrl', 'SPACE', 'Alt Gr', 'Ctrl', '←', '↓', '↑', '→']
INTRO_KEY = '↲'
COLORS = {'background': (0.5, 0.5, 0.5),
          'key-button': (0.7, 0.7, 0.7),
          'key-letter': (1, 1, 1)}


class Key():
    def __init__(self, key):

        self.width = 0
        self.height = 0
        self._size = (0, 0)
        self._pos = (0, 0)
        self.key = key
        self.x = 0
        self.y = 0
        self.context = None
        self.mayus = 'StartOnly'
        self.font_size = 20

    def set_context(self, context):
        self.context = context

    def render(self):
        print self.key
        if self.key in KEYS1:
            _list = KEYS1
            n = 1

        elif self.key in KEYS2:
            _list = KEYS2
            n = 2

        elif self.key in KEYS3:
            _list = KEYS3
            n = 3

        elif self.key in KEYS4:
            _list = KEYS4
            n = 4

        elif self.key in KEYS5:
            _list = KEYS5
            n = 5

        self.width = (self._size[0]) / float(len(_list)) * self._increment
        self.height = self._size[1] / 6.0 * self._increment
        self.x = self.width * _list.index(self.key) + self._pos[0]
        self.y = self.height * n + self._center[1] - self._mouse_position[1] * self._increment
        self.font_size = self._size[0] / len(_list)

        self.context.set_source_rgba(*COLORS['key-button'])
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

        self.context.set_font_size(self.font_size)
        self.context.select_font_face(*FONT)
        x = self.x + (self.width / 2.0) - (self.context.text_extents(self.key)[2] / 2.0)
        y = self.y + (self.height / 2.0) + (self.context.text_extents(self.key)[3] / 2.0)
        self.context.set_source_rgba(*COLORS['key-letter'])
        self.context.move_to(x, y)
        self.context.show_text(self.key.upper() if self.mayus else self.key.lower())


class KeyBoard(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.context = None
        self.center = (0, 0)
        self.mouse_position = (0, 0)
        self.keyboard_size = (0, 0)
        self.size = (0, 0)
        self.keys = [Key(x) for x in (KEYS1 + KEYS2 + KEYS3 + KEYS4 + KEYS5)]
        self.mayus = 'StartOnly'  # 'None', 'StartOnly', 'ForEver'
        self.increment = INCREMENTO
        self.x = 0
        self.y = 0
        self.moving = True

        self.set_size_request(640, 480)
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('motion-notify-event', self.__motion_notify_event)
        #self.connect('button-press-event', self.__button_press_event_cb)

    def __draw_cb(self, widget, context):
        atn = self.get_allocation()

        self.context = context
        self.size = (atn.width, atn.height)
        self.keyboard_size = (atn.width * self.increment, atn.height * self.increment)
        self.center = (atn.width / 2.0, atn.height / 2.0)

        self.render()

    def __motion_notify_event(self, widget, event):
        self.mouse_position = (event.x, event.y)
        self.calculate_pos()
        self.render()
        GObject.idle_add(self.queue_draw)

    def calculate_pos(self):
        if self.moving:
            self.x = self.center[0] - self.mouse_position[0] * self.increment
            self.y = self.center[1] - self.mouse_position[1] * self.increment

            if self.x + self.size[0] > self.keyboard_size[0]:
                self.x = self.keyboard_size[0] - self.size[0]

            if self.y + self.size[1] > self.keyboard_size[1]:
                self.y = self.keyboard_size[1] - self.size[1]

    def render(self):
        # Si cada tecla tiene su propia x e y no habran problemas
        self.render_background()
        self.render_keys()

    def render_background(self):
        self.context.set_source_rgba(*COLORS['background'])
        self.context.rectangle(0, 0, self.size[0], self.size[1])
        self.context.fill()

    def render_keys(self):
        for key in self.keys:
            key.context = self.context
            key.mayus = self.mayus
            key._size = self.size
            key._pos = (self.x, self.y)
            key._increment = self.increment
            key._center = self.center
            key._mouse_position = self.mouse_position
            key.render()


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.area = KeyBoard()

        self.connect('destroy', Gtk.main_quit)

        self.add(self.area)
        self.show_all()


if __name__ == '__main__':
    Window()
    Gtk.main()
