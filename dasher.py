#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import cairo
import random

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

LETTERS = [chr(x) for x in range(65, 91)]
COLORS = {'pink': (1.0, 0.6823529411764706, 0.7254901960784313),
          'red': (1.0, 0, 0),
          'green': (0.0, 0.7843137254901961, 0.0),
          'sky-blue': (0.5294117647058824, 0.807843137254902, 1.0),
          'white': (1.0, 1.0, 1.0)}

# Color amarillo para todas las letras
# Teclado al estilo dasher, pero con teclas similares a las fisicas


class LetterBox(GObject.GObject):

    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, []),
        'unselected': (GObject.SIGNAL_RUN_FIRST, None, []),
        }

    def __init__(self, letter, father):
        GObject.GObject.__init__(self)

        self.letter = letter
        self.color = COLORS['pink']
        _width = father.width
        _height = father.height
        self.width = _width / 2.0
        self.height = _height / 2.0
        self.x = self.width / 2.0
        self.y = self.height / (float(len(LETTERS)) * LETTERS.index(letter) + 1)
        self.context = None
        self.selected = False
        self.boxes = []  # LetterBox children only
        self.father = father

    def set_context(self, context):
        self.context = context

    def render(self):
        self.width = self.father.width / 2.0
        self.height = self.father.height / 2.0
        self.x = self.father.x + self.width
        self.y = self.father.y

        self.paint()
        self.check_selected()

    def set_pos(self, x, y, center_y, width, height):
        self.x = x
        self.y = y

        self.width = width
        self.height = height
        self.paint()

    def paint(self):
        self.context.move_to(self.x, self.y)
        self.context.set_source_rgba(*self.color)
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

    def check_selected(self):
        if self.x < self._center[0]:
            if not self.selected:
                self.emit('selected')

        elif self.x > self._center[0]:
            if self.selected:
                self.emit('unselected')


class InitBox(GObject.GObject):

    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, []),
        'unselected': (GObject.SIGNAL_RUN_FIRST, None, []),
        }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.letter = None
        self.inc = 50
        self._center = (self.inc, 0)
        self._width = 0
        self._height = 0
        self.width = 0
        self.height = 200
        self.x = self._center[0]
        self.y = self._center[1]
        self.color = (0.7058823529411765, 0.9333333333333333, 0.7058823529411765)
        self.selected = False
        self.boxes = []

    def set_context(self, context):
        self.context = context

    def set_center(self, x, y):
        if self._center == (self.inc, 0):
            self._center = x + self.inc, y
            self.x = x + self.inc
            self.y = y

    def move(self, x, y):
        if str(x).startswith('0.'):
            x = 0
        if str(y).startswith('0.'):
            y = 0

        self.x += x
        self.y += y

        if self.y + self.height < self._center[1]:
            self.y = self._center[1] - self.height
        elif self.y > self._center[1]:
            self.y = self._center[1]

        self.width = self._width / 4.0 - self.x + self.inc + self._center[0]
        self.height = self.width

        if self.width < self._width / 4.0:
            self.width = self._width / 4.0
            self.x -= x

        self.paint()
        self.check_selected()

    def paint(self):
        self.context.set_source_rgba(*self.color)
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

    def check_selected(self):
        if self.x < self._center[0]:
            if not self.selected:
                self.selected = True
                self.emit('selected')

        elif self.x > self._center[0]:
            if self.selected:
                self.selected = False
                self.emit('unselected')


class Letters(InitBox):

    def __init__(self, father):
        InitBox.__init__(self)

        self.father = father
        self.color = COLORS['green']
        self.selected = False

    def render(self):
        self.width = self.father.width / 2.0
        self.height = self.father.height / 2.0
        self.x = self.father.x + self.width
        self.y = self.father.y

        self.paint()
        self.check_selected()

    def check_selected(self):
        _x, _y = self._center
        if _x > self.x and _y > self.y and _y < self.x + self.height:
            if not self.selected:
                self.selected = True
                self.emit('selected')

        else:
            if self.selected:
                self.selected = False
                self.emit('unselected')


class Character(InitBox):

    def __init__(self):
        InitBox.__init__(self)


class Area(Gtk.DrawingArea):

    __gsignals__ = {
        'text-changed': (GObject.SIGNAL_RUN_FIRST, None, [])
        }

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.width = 0
        self.height = 0
        self.mouse_pos = (0, 0)
        self.center = (0, 0)
        self.distance = 0
        self.context = None
        self.update_loop = None
        self.key_loop = None
        self.text = None
        self.moving = False
        self.init_box = InitBox()
        self.actual_box = self.init_box
        self.boxes = []  # All letter boxes

        self.set_size_request(500, 500)
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('motion-notify-event', self.__motion_notify_event)
        self.connect('button-press-event', self.__button_press_event_cb)
        self.init_box.connect('selected', self.box_selected)
        self.init_box.connect('unselected', self.box_unselected)

    def box_selected(self, box):
        # Agregar 2 cajas:
        # 1) Letras
        # 2) Caracteres
        if isinstance(box, Letters):
            box.selected = True
            for letter in LETTERS:
                _box = LetterBox(letter, box)
                _box.set_context(self.context)
                _box.connect('selected', self.box_selected)
                #_box.connect('unselected', self.box_unselected)
                self.boxes.append(_box)

        elif isinstance(box, InitBox):
            _box = Letters(self.actual_box)
            _box.selected = True
            _box.connect('selected', self.box_selected)
            #_box.connect('unselected', self.box_unselected)
            self.boxes.append(_box)

    def box_unselected(self, box):
        if not isinstance(box, InitBox):
            for _box in box.boxes:
                self.boxes.remove(_box)

            del box.boxes
            box.boxes = []

        else:
            del self.boxes
            self.boxes = []

    def __draw_cb(self, widget, context):
        allocation = self.get_allocation()
        self.width = allocation.width
        self.height = allocation.height
        self.center = (self.width / 2.0, self.height / 2.0)
        self.context = context

        self.init_box.context = context
        self.init_box.set_center(*self.center)

        self.render()

    def __motion_notify_event(self, widget, event):
        self.mouse_pos = (event.x, event.y)
        self.render()

    def __button_press_event_cb(self, widget, event):
        self.moving = not self.moving

    def render(self):
        self.render_background()
        self.move()
        self.render_lines()
        self.render_line_to_mouse()

    def render_background(self):
        self.context.set_source_rgba(1, 1, 1)
        self.context.rectangle(0, 0, self.width, self.height)
        self.context.fill()

    def render_lines(self):
        self.context.set_line_width(1)
        self.context.set_source_rgba(0, 0, 0)
        self.context.move_to(self.center[0], 0)
        self.context.line_to(self.center[0], self.height)
        self.context.move_to(self.center[0] - self.center[0] / 8.0, self.center[1])
        self.context.line_to(self.center[0] + self.center[0] / 8.0, self.center[1])
        self.context.stroke()

    def render_line_to_mouse(self):
        max_x = self.center[0] + self.width / 4.0
        min_x = self.width / 4.0
        x = self.mouse_pos[0]
        y = self.mouse_pos[1]
        self.distance = self.get_distance(self.center, (x, y))

        if x > self.center[0]:
            x = x if x < max_x else max_x
        elif x < self.center[0]:
            x = x if x > min_x else min_x

        self.context.set_source_rgba(1, 0, 0)
        self.context.move_to(*self.center)
        self.context.line_to(x, y)
        self.context.stroke()
        GObject.idle_add(self.queue_draw)

    def move(self):
        x = (self.center[0] - self.mouse_pos[0]) / 10.0
        y = (self.center[1] - self.mouse_pos[1]) / 10.0
        self.init_box.context = self.context

        if self.moving:
            self.init_box._width = self.width
            self.init_box._height = self.height
            self.init_box._center = self.center
            self.init_box.move(x, y)
        else:
            self.init_box.paint()

        box_separation = 1
        box_size = self.init_box.height / (len(LETTERS)) - box_separation
        _x = self.init_box.x + self.init_box.width / 2.0
        _y = self.init_box.y

        for box in self.boxes:
            # FIXME: hacer que cada caja tenga un padre, y tomar las medidas de este padre
            x = _x
            y = _y

            _y = y + box_size + box_separation
            box.set_context(self.context)

            if self.moving:
                #box.move(x, y, self.center[1])
                #box.set_pos(x, y, self.center[1], self.init_box.width / 2.0, box_size)
                box._center = self.center
                box.context = self.context
                box.render()
            else:
                box.paint()

    def get_distance(self, (x1, y1), (x2, y2)):
        return math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2)


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.area = Area()

        self.connect('destroy', Gtk.main_quit)

        self.add(self.area)
        self.show_all()


if __name__ == '__main__':
    Window()
    Gtk.main()
