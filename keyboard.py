#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import globals as G

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.colorbutton import ColorToolButton
from sugar3.activity.widgets import _create_activity_icon as ActivityIcon


class Key(GObject.GObject):

    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, []),
        'unselected': (GObject.SIGNAL_RUN_FIRST, None, []),
        }

    def __init__(self, lower_key, mayus_key, context):
        GObject.GObject.__init__(self)

        self.width = 0
        self.height = 0
        self._size = (0, 0)
        self._pos = (0, 0)
        self.lower_key = lower_key
        self.mayus_key = mayus_key
        self.x = 0
        self.y = 0
        self.context = context
        self.mayus = 'StartOnly'
        self.font_size = 0
        self.selected = False
        self.normal_color = G.COLORS['key-button']
        self.selected_color = G.COLORS['key-selected']
        self.label_color = G.COLORS['key-letter']

    def render(self):
        if self.lower_key == G.INTRO_KEY:
            self.render_as_intro_key()
            return

        else:
            _list, n = G.get_in_list(self.lower_key)

        idx = _list.index(self.lower_key)

        self.width = (self._size[0]) / float(len(_list)) * self._increment
        self.height = self._size[1] / 6.0 * self._increment
        self.x = self.width * idx + self._pos[0]
        self.y = self.height * n + \
            self._center[1] - self._mouse_position[1] * self._increment
        self.font_size = self.height / 6 * 5.0

        if self.selected:
            self.context.set_source_rgba(*self.selected_color)
        else:
            self.context.set_source_rgba(*self.normal_color)

        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

        self.render_label()
        self.check_selected()

    def render_label(self):
        key = G.get_mayus_key(self.mayus, self._text, self)
        if key == 'SPACE':
            return

        self.context.set_font_size(self.font_size)
        self.context.select_font_face(*G.FONT)
        x = self.x + (
            self.width / 2.0) - (self.context.text_extents(key)[3] / 2.0)
        y = self.y + (
            self.height / 2.0) + (self.context.text_extents(key)[4] / 2.0)
        if self.lower_key == '-':
            x -= self.context.text_extents(key)[3] * 3.0

        elif self.lower_key == '.':
            x -= self.context.text_extents(key)[3] * 1.5
            y += (self.context.text_extents(key)[4] / 4.0)

        elif self.lower_key == ',':
            x -= self.context.text_extents(key)[3] / 1.5

        self.context.set_source_rgba(*self.label_color)
        self.context.move_to(x, y)

        self.context.show_text(key)

    def render_as_intro_key(self):
        self.font_size = self._size[0] / len(G.KEYS1()) * self._increment
        self.width = \
            self._size[0] / float(len(G.KEYS1()) - 1) * self._increment
        self.height = self._size[1] / 5.0 * self._increment
        self.x = self.width * G.KEYS1().index(G.DEL_KEY) + self._pos[0] + 20
        self.y = self.height * 2 + self._center[1] - \
            self._mouse_position[1] * self._increment

        key = G.get_mayus_key(self.mayus, self._text, self)

        if self.selected:
            self.context.set_source_rgba(*self.selected_color)
        else:
            self.context.set_source_rgba(*self.normal_color)

        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.fill()

        self.context.set_font_size(self.font_size)
        x = self.x + (
            self.width / 2.0) - (self.context.text_extents(key)[2] / 2.0)
        y = self.y + (
            self.height / 2.0) + (self.context.text_extents(key)[3] / 2.0)
        self.context.set_source_rgba(*self.label_color)
        self.context.move_to(x, y)
        self.context.show_text(key)

        self.check_selected()

    def check_selected(self):
        within = self._mouse_position[0] > self.x and \
            self._mouse_position[0] < self.x + self.width and \
            self._mouse_position[1] > self.y and \
            self._mouse_position[1] < self.y + self.height

        if within and not self.selected:
            self.selected = True
            self.emit('selected')

        elif not within and self.selected:
            self.selected = False
            self.emit('unselected')


class KeyBoard(Gtk.DrawingArea):

    __gsignals__ = {
        'text-changed': (GObject.SIGNAL_RUN_FIRST, None, [object])
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
        self.increment = 2
        self.x = 0
        self.y = 0
        self.selected_key = None
        self.text = ''
        self.normal_color = G.COLORS['key-button']
        self.selected_color = G.COLORS['key-selected']
        self.label_color = G.COLORS['key-letter']
        self.background_color = G.COLORS['background']

        self.set_size_request(640, 480)
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.SCROLL_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('motion-notify-event', self.__motion_notify_event)
        self.connect('button-release-event', self.__button_release_event_cb)
        self.connect('scroll-event', self.__scroll_event)

    def __draw_cb(self, widget, context):
        atn = self.get_allocation()

        self.context = context
        self.size = (atn.width, atn.height)
        self.keyboard_size = (
            atn.width * self.increment, atn.height * self.increment)
        self.center = (atn.width / 2.0, atn.height / 2.0)

        l1, l2 = G.KEYS1() + G.KEYS2()
        _l1, _l2 = G.KEYS3() + G.KEYS4()
        l = l1 + _l1 + ['SPACE']

        if not self.keys:
            for lowed in l:
                _list, n = G.get_in_list(lowed)
                upped = _list[lowed]
                key = Key(lowed, upped, self.context)
                key.connect('selected', self.__selected_key)
                key.connect('unselected', self.__unselected_key)
                self.keys.append(key)

        self.render()

    def __motion_notify_event(self, widget, event):
        self.mouse_position = (event.x, event.y)
        self.calculate_pos()
        self.render()
        GObject.idle_add(self.queue_draw)

    def __button_release_event_cb(self, widget, event):
        if event.button == 1:
            if self.selected_key:
                if self.selected_key.lower_key in G.MAYUS_KEYS.keys():
                    self.next_mayus(self.selected_key)
                    return

                self.emit('text-changed', self.selected_key)

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
        num, mayus = G.MAYUS_KEYS[key.lower_key]
        d = {0: 1, 1: 2, 2: 0}
        num = d[num]

        if num == 0:
            self.mayus = 'Never'
            simbol = '↾'
        elif num == 1:
            self.mayus = 'StartOnly'
            simbol = '⇧'
        elif num == 2:
            self.mayus = 'Forever'
            simbol = '⇈'

        key.lower_key = simbol
        key.mayus_key = simbol
        G.set_mayus_key(simbol)

        GObject.idle_add(self.queue_draw)

    def calculate_pos(self):
        self.x = self.center[0] - self.mouse_position[0] * self.increment
        self.y = self.center[1] - self.mouse_position[1] * self.increment

    def render(self):
        self.render_background()
        self.render_keys()

    def render_background(self):
        self.context.set_source_rgba(*self.background_color)
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
            key.normal_color = self.normal_color
            key.selected_color = self.selected_color
            key.label_color = self.label_color

            key.render()

    def set_text(self, text):
        self.text = text
        self.render_keys()

    def __selected_key(self, key):
        self.selected_key = key

    def __unselected_key(self, key):
        if self.selected_key == key:
            self.selected_key = None


class DasherActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.text = ''

        self.view = Gtk.TextView()
        self.buffer = self.view.get_buffer()
        self.area = KeyBoard()
        vbox = Gtk.VBox()
        scrolled = Gtk.ScrolledWindow()

        scrolled.set_size_request(-1, 100)
        self.view.modify_font(Pango.FontDescription('25'))

        self.connect('destroy', Gtk.main_quit)
        self.buffer.connect('changed', self._buffer_changed)
        self.buffer.connect('notify::cursor-position', self._cursor_moved)
        self.area.connect('text-changed', self.text_changed)
        self.area.connect('motion-notify-event', self.__motion_notify_event)

        self.load_data()
        self.make_toolbar()

        scrolled.add(self.view)
        vbox.pack_start(scrolled, False, False, 0)
        vbox.pack_start(self.area, True, True, 0)
        self.set_canvas(vbox)
        self.show_all()

    def _buffer_changed(self, _buffer):
        start = _buffer.get_start_iter()
        end = _buffer.get_iter_at_mark(_buffer.get_selection_bound())
        self.text = _buffer.get_text(start, end, 0)
        self.area.set_text(self.text)

    def _cursor_moved(self, _buffer, event):
        self._buffer_changed(_buffer)

    def text_changed(self, widget, key):
        text = key.lower_key
        if text != G.DEL_KEY:
            text = G.get_mayus_key(self.area.mayus, self.text, key)
            if text == 'SPACE':
                text = ' '
            elif text == G.INTRO_KEY:
                text = '\n'
            elif text == G.TAB_KEY:
                text = '\t'

            self.buffer.insert_at_cursor(text)

        else:
            if self.buffer.get_selection_bounds():
                start, end = self.buffer.get_bounds()
                _end, _start = self.buffer.get_selection_bounds()
                offset = _end.get_offset()

                text = self.buffer.get_text(
                    start, _end, 0) + self.buffer.get_text(_start, end, 0)
                self.buffer.set_text(text)
                self.buffer.place_cursor(
                    self.buffer.get_iter_at_offset(offset))

            else:
                _end = self.buffer.get_iter_at_mark(
                    self.buffer.get_selection_bound())
                self.buffer.backspace(_end, True, True)

    def copy_text(self, widget=None):
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text(start, end, 0)
        self.clipboard.set_text(text, -1)

    def remove_text(self, widget=None):
        self.buffer.set_text('')

    def cut_text(self, text):
        self.copy_text()
        self.remove_text()

    def __motion_notify_event(self, widget, event):
        #for button in self.color_palettes:
        #    palette = button._palette
        #    if palette and palette.is_up():
        #        palette.down()
        pass

    def make_toolbar(self):
        def make_separator(expand=False, size=0):
            separator = Gtk.SeparatorToolItem()
            separator.set_size_request(size, -1)
            if expand:
                separator.set_expand(True)

            if expand or size:
                separator.props.draw = False

            return separator

        self.color_palettes = []

        toolbar_box = ToolbarBox()
        toolbar = toolbar_box.toolbar

        activity_button = ToolButton()
        activity_button.set_icon_widget(ActivityIcon(None))
        toolbar.insert(activity_button, -1)

        toolbar.insert(make_separator(size=30), -1)

        button_copy = ToolButton(Gtk.STOCK_COPY)
        button_copy.set_tooltip('Copy the text.')
        button_copy.connect('clicked', self.copy_text)
        toolbar.insert(button_copy, -1)

        button_cut = ToolButton('cut')
        button_cut.set_tooltip('Cut the text.')
        button_cut.connect('clicked', self.cut_text)
        toolbar.insert(button_cut, -1)

        button_remove = ToolButton(Gtk.STOCK_REMOVE)
        button_remove.set_tooltip('Remove all the text.')
        button_remove.connect('clicked', self.remove_text)
        toolbar.insert(button_remove, -1)

        toolbar.insert(make_separator(size=30), -1)

        button_normal = ColorToolButton()
        button_normal.set_color(G.cairo_to_gdk(self.area.normal_color))
        button_normal.set_title('Choose a color for the buttons.')
        button_normal.connect('color-set', self._normal_color_changed)
        toolbar.insert(button_normal, -1)

        self.color_palettes.append(button_normal)

        button_selected = ColorToolButton()
        button = button_selected.get_child()
        button_selected.set_color(G.cairo_to_gdk(self.area.selected_color))
        button_selected.set_title('Choose a color for the selected buttons.')
        button_selected.connect('color-set', self._selected_color_changed)
        toolbar.insert(button_selected, -1)

        self.color_palettes.append(button_selected)

        button_labels = ColorToolButton()
        button_labels.set_color(G.cairo_to_gdk(self.area.label_color))
        button_labels.set_title('Choose a color for the labels buttons.')
        button_labels.connect('color-set', self._label_color_changed)
        toolbar.insert(button_labels, -1)

        self.color_palettes.append(button_labels)

        button_background = ColorToolButton()
        button_background.set_color(G.cairo_to_gdk(self.area.background_color))
        button_background.set_title('Choose a color for the background.')
        button_background.connect('color-set', self._background_color_changed)
        toolbar.insert(button_background, -1)

        self.color_palettes.append(button_background)
        toolbar.insert(make_separator(expand=True), -1)

        stop_button = ToolButton('activity-stop')
        stop_button.connect('clicked', lambda w: self.close())
        stop_button.props.accelerator = '<Ctrl>Q'
        toolbar.insert(stop_button, -1)

        self.set_toolbar_box(toolbar_box)

    def _normal_color_changed(self, widget):
        self.area.normal_color = G.gdk_to_cairo(widget.get_color())

    def _selected_color_changed(self, widget):
        self.area.selected_color = G.gdk_to_cairo(widget.get_color())

    def _label_color_changed(self, widget):
        self.area.label_color = G.gdk_to_cairo(widget.get_color())

    def _background_color_changed(self, widget):
        self.area.background_color = G.gdk_to_cairo(widget.get_color())

    def load_data(self):
        if 'normal-color' in self.metadata:
            normal_color = G.get_color(self.metadata['normal-color'])
            key_selected_color = G.get_color(self.metadata['key-selected-color'])
            key_label_color = G.get_color(self.metadata['key-label-color'])
            background_color = G.get_color(self.metadata['background-color'])

            self.area.normal_color = normal_color
            self.area.selected_color = key_selected_color
            self.area.label_color = key_label_color
            self.area.background_color = background_color
            self.area.increment = float(self.metadata['increment'])
            self.buffer.set_text(str(eval(self.metadata['text'])))

        else:
            self.area.normal_color = G.COLORS['key-button']
            self.area.selected_color = G.COLORS['key-selected']
            self.area.label_color = G.COLORS['key-letter']
            self.area.background_color = G.COLORS['background']

    def write_file(self, file_path):
        normal_color = json.dumps(list(self.area.normal_color))
        key_selected_color = json.dumps(list(self.area.selected_color))
        key_label_color = json.dumps(list(self.area.label_color))
        background_color = json.dumps(list(self.area.background_color))
        _iters = (self.buffer.get_start_iter(), self.buffer.get_end_iter(), 0)
        text = self.buffer.get_text(*_iters)

        self.metadata['normal-color'] = normal_color
        self.metadata['key-selected-color'] = key_selected_color
        self.metadata['key-label-color'] = key_label_color
        self.metadata['background-color'] = background_color
        self.metadata['increment'] = self.area.increment
        self.metadata['text'] = json.dumps(text)

    def set_normal_color(self, button):
        self.area.normal_color = G.gdk_to_cairo(button.get_color())
