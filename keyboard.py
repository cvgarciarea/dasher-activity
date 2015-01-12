#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cairo
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

FONT = ('Monospace', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
KEYS1 = [str(x) for x in range(1, 10)] + ['0', '←']
KEYS2 = ['⇄', 'q', 'w', 'e', 'r', 't', 'y', 'i', 'o', 'p']
KEYS3 = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '{', '}']
KEYS4 = ['⇧', '<', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-']
KEYS5 = ['SPACE']
INTRO_KEY = '↲'
DEL_KEY = '←'
TAB_KEY = '⇄'
COLORS = {'background': (0.5, 0.5, 0.5),
          'key-button': (0.7, 0.7, 0.7),
          'key-letter': (1, 1, 1),
          'key-selected': (0.6, 0.6, 0.6)}

MAYUS_KEYS = {'↾': [0, 'Never'],
              '⇧': [1, 'StartOnly'],
              '⇈': [2, 'Forever']}



class Key(GObject.GObject):

    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, []),
        'unselected': (GObject.SIGNAL_RUN_FIRST, None, []),
        }

    def __init__(self, key, context):
        GObject.GObject.__init__(self)

        self.width = 0
        self.height = 0
        self._size = (0, 0)
        self._pos = (0, 0)
        self.key = key
        self.real_key = key
        self.x = 0
        self.y = 0
        self.context = context
        self.mayus = 'StartOnly'
        self.font_size = 0
        self.selected = False
        self.color = COLORS['key-button']

    def render(self):

        if self.real_key in KEYS1:
            _list = KEYS1
            n = 1
        elif self.real_key in KEYS2:
            _list = KEYS2
            n = 2
        elif self.real_key in KEYS3:
            _list = KEYS3
            n = 3
        elif self.real_key in KEYS4 or self.key in MAYUS_KEYS:
            _list = KEYS4
            n = 4
        elif self.real_key in KEYS5:
            _list = KEYS5
            n = 5
        else:  # Intro key
            self.render_as_intro_key()
            return

        self.width = (self._size[0]) / float(len(_list)) * self._increment
        self.height = self._size[1] / 6.0 * self._increment
        if self.real_key in _list:
            self.x = self.width * _list.index(self.real_key) + self._pos[0]
        else:
            self.x = self._pos[0]

        self.y = self.height * n + self._center[1] - self._mouse_position[1] * self._increment
        self.font_size = self._size[0] / len(_list)

        self.context.set_source_rgba(*self.color)
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

        self.context.set_font_size(self.font_size)
        self.context.select_font_face(*FONT)
        x = self.x + (self.width / 2.0) - (self.context.text_extents(self.key)[2] / 2.0)
        y = self.y + (self.height / 2.0) + (self.context.text_extents(self.key)[3] / 2.0)
        self.context.set_source_rgba(*COLORS['key-letter'])
        self.context.move_to(x, y)

        if self.real_key != 'SPACE':
            if self.mayus == 'Forever':
                self.key = self.key.upper()

            elif self.mayus == 'StartOnly':
                if self._text.endswith('\n') or self._text.strip().endswith('.') or not self._text:
                    self.key = self.key.upper()
                else:
                    self.key = self.key.lower()

            elif self.mayus == 'Never':
                self.key = self.key.lower()

            self.context.show_text(self.key)

        self.check_selected()

    def render_as_intro_key(self):
        self.font_size = self._size[0] / len(KEYS1)
        self.width = self._size[0] / float(len(KEYS1) - 1) * self._increment
        self.height = self._size[1] / 5.0 * self._increment
        self.x = self.width * KEYS1.index('←') + self._pos[0] + 20
        self.y = self.height * 2 + self._center[1] - self._mouse_position[1] * self._increment

        self.context.set_source_rgba(*self.color)
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

        self.context.set_font_size(self.font_size)
        x = self.x + (self.width / 2.0) - (self.context.text_extents(self.key)[2] / 2.0)
        y = self.y + (self.height / 2.0) + (self.context.text_extents(self.key)[3] / 2.0)
        self.context.set_source_rgba(*COLORS['key-letter'])
        self.context.move_to(x, y)
        self.context.show_text(self.key)

        self.check_selected()

    def check_selected(self):
        within = self._mouse_position[0] > self.x and \
            self._mouse_position[0] < self.x + self.width and \
            self._mouse_position[1] > self.y and \
            self._mouse_position[1] < self.y + self.height

        if within and not self.selected:
            self.selected = True
            self.color = COLORS['key-selected']
            self.emit('selected')

        elif not within and self.selected:
            self.selected = False
            self.color = COLORS['key-button']
            self.emit('unselected')


class KeyBoard(Gtk.DrawingArea):

    __gsignals__ = {
        'text-changed': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.context = None
        self.center = (0, 0)
        self.mouse_position = (0, 0)
        self.keyboard_size = (0, 0)
        self.size = (0, 0)
        self.keys = []
        self.mayus = 'StartOnly'  # 'Never', 'StartOnly', 'Forever'
        self.increment = 1
        self.x = 0
        self.y = 0
        self.text = ''
        self.selected_key = None

        # FIXME: agregar incrementar tamaño al hacer scroll up, lo mismo para disminuir
        self.set_size_request(640, 480)
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.SCROLL_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('motion-notify-event', self.__motion_notify_event)
        self.connect('button-press-event', self.__button_press_event_cb)
        self.connect('scroll-event', self.__scroll_event)

    def __draw_cb(self, widget, context):
        atn = self.get_allocation()

        self.context = context
        self.size = (atn.width, atn.height)
        self.keyboard_size = (atn.width * self.increment, atn.height * self.increment)
        self.center = (atn.width / 2.0, atn.height / 2.0)

        if not self.keys:
            for x in KEYS1 + KEYS2 + KEYS3 + KEYS4 + KEYS5 + [INTRO_KEY]:
                key = Key(x, self.context)
                key.connect('selected', self.__selected_key)
                key.connect('unselected', self.__unselected_key)
                self.keys.append(key)

        self.render()

    def __motion_notify_event(self, widget, event):
        self.mouse_position = (event.x, event.y)
        self.calculate_pos()
        self.render()
        GObject.idle_add(self.queue_draw)

    def __button_press_event_cb(self, widget, event):
        # FIXME: button1: add key to text, button3: stop moviment
        if event.button == 1:
            if self.selected_key:
                text = self.selected_key.key
                if text == 'SPACE':
                    text = ' '
                elif text == INTRO_KEY:
                    text = '\n'
                elif text == TAB_KEY:
                    text = '\t'
                elif text in MAYUS_KEYS.keys():
                    self.next_mayus(self.selected_key)
                    return
                elif text == DEL_KEY:
                    if len(self.text):
                        self.text = self.text[:-1]
                        self.emit('text-changed', self.text)
                    return

                self.text += text
                self.emit('text-changed', self.text)

    def __scroll_event(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            if self.increment < 5.0:
                self.increment += 0.01
        elif event.direction == Gdk.ScrollDirection.DOWN:
            if self.increment > 1.01:
                self.increment -= 0.01

        self.calculate_pos()
        self.render()
        GObject.idle_add(self.queue_draw)

    def next_mayus(self, key):
        n, mayus = MAYUS_KEYS[key.key]
        if n == 2:
            n = 0
        else:
            n += 1

        for s, l in MAYUS_KEYS.items():
            if n == l[0]:
                key.key = s
                KEYS4[0] = s
                self.mayus = l[1]

    def calculate_pos(self):
        self.x = self.center[0] - self.mouse_position[0] * self.increment
        self.y = self.center[1] - self.mouse_position[1] * self.increment

        if self.x + self.size[0] > self.keyboard_size[0]:
            self.x = self.keyboard_size[0] - self.size[0]

        if self.y + self.size[1] > self.keyboard_size[1]:
            self.y = self.keyboard_size[1] - self.size[1]

    def render(self):
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
            key._text = self.text

            key.render()

    def __selected_key(self, key):
        self.selected_key = key

    def __unselected_key(self, key):
        if self.selected_key == key:
            self.selected_key = None


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.entry = Gtk.Entry()
        self.area = KeyBoard()
        vbox = Gtk.VBox()

        self.connect('destroy', Gtk.main_quit)
        self.area.connect('text-changed', self.text_changed)

        vbox.pack_start(self.entry, False, False, 0)
        vbox.pack_start(self.area, True, True, 0)
        self.add(vbox)
        self.show_all()

    def text_changed(self, widget, text):
        self.entry.set_text(text)


if __name__ == '__main__':
    Window()
    Gtk.main()
