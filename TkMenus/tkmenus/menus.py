########################################################################################################################
#    File: menus.py
#  Author: Dan Huckson, https://github.com/unodan
#    Date: 2018-06-29
########################################################################################################################
from os import path, getcwd
from platform import system, release
from importlib import import_module

from tkinter import Menu, PhotoImage
from tkinter.font import Font


class MenuItem:
    def __init__(self, parent, json, **kwargs):
        self.parent = parent
        self.has_children = False

        self.font = json.get('font')
        self.type = json.get('type', 'item')
        self.label = json.get('label')
        self.state = json.get('state')
        self.value = json.get('value')
        self.index = kwargs.get('index')
        self.command = json.get('command')
        self.onvalue = json.get('onvalue', True)
        self.offvalue = json.get('offvalue', False)
        self.variable = json.get('variable')
        self.compound = json.get('compound', 'left')
        self.underline = json.get('underline', 0)
        self.foreground = json.get('foreground')
        self.background = json.get('background')
        self.accelerator = json.get('accelerator')
        self.activeforeground = json.get('activeforeground')
        self.activebackground = json.get('activebackground')

        if isinstance(self.font, dict):
            self.font = Font(
                family=self.font.get('family'),
                size=self.font.get('size'),
                weight=self.font.get('weight', 'normal'),
                slant=self.font.get('slant', 'roman'),
                underline=self.font.get('underline', False),
                overstrike=self.font.get('overstrike', False)
            )
        self.image = PhotoImage(file=path.join(getcwd(), 'tkmenus', 'images', json.get('image', 'blank-21x16.png')))

        kwargs = {
            'font': self.font,
            'label': self.label,
            'state': self.state,
            'index': self.index,
            'command': self.command,
            'variable': self.variable,
            'compound': self.compound,
            'underline': self.underline,
            'foreground': self.foreground,
            'background': self.background,
            'accelerator': self.accelerator,
            'activeforeground': self.activeforeground,
            'activebackground': self.activebackground,
        }

        if self.command:
            cmd = self.command.split('.')

            if len(cmd) == 1:
                file = 'main'
                command = cmd[0]
            else:
                file, command = cmd

            module = import_module(file)
            self.command = getattr(module, command, None)

        menu_type = json.get('type')
        if menu_type == 'separator':
            func = parent.insert_separator if self.index is not None else parent.add_separator
            func(index=self.index, background=self.background)
        elif menu_type == 'checkbutton':
            func = parent.insert_checkbutton if self.index is not None else parent.add_checkbutton
            func(**{**kwargs, **{'onvalue': self.onvalue, 'offvalue': self.offvalue}})
        elif menu_type == 'radiobutton':
            func = parent.insert_radiobutton if self.index is not None else parent.add_radiobutton
            func(**{**kwargs, **{'value': self.value}})
        else:
            func = parent.insert_command if self.index is not None else parent.add_command
            func(**{**kwargs, **{'image': self.image, 'command': self.command}})

    def cget(self, attribute):
        return getattr(self, attribute, None)

    def config(self, **kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

        if self.index == 0 and self.parent.tearoff:
            self.index = 1

        args = dict(kwargs)
        args.pop('bd', None)
        args.pop('relief', None)
        if self.type != 'separator':
            self.parent.entryconfig(self.index, **args)
        else:
            self.parent.entryconfig(self.index, background=kwargs.get('background'))


class Menus(Menu):
    def __init__(self, parent, **kwargs):
        self.index = kwargs.pop('index', None)
        super().__init__(parent, **kwargs)
        self.__index = 0

        self.key = None
        self.type = None
        self.items = {}
        self.parent = parent
        self.platform = (system(), release())

        self.bd = None
        self.font = None
        self.label = None
        self.image = None
        self.index = None
        self.state = None
        self.relief = None
        self.tearoff = None
        self.compound = None
        self.underline = None
        self.foreground = None
        self.background = None
        self.activeforeground = None
        self.activebackground = None

    def menu(self, uri):
        return self.get_child(uri)

    def populate(self, children):
        for key, child in children.items():
            self.add_child(key, child)

        return self

    def get_child(self, uri):
        uri = uri.replace('\\', '/')

        if '/' in uri:
            def parse(parent, uri_part):
                parts = uri_part.split('/', 1)
                child = parent.get_child(parts[0])

                if len(parts) > 1:
                    child = parse(child, parts[1])
                return child

            return parse(self, uri)

        return self.items.get(uri, None)

    def add_child(self, key, json, **kwargs):
        font = kwargs.get('font', json.get('font', None))

        if isinstance(font, dict):
            font = Font(
                family=font.get('family'),
                size=font.get('size'),
                weight=font.get('weight', 'normal'),
                slant=font.get('slant', 'roman'),
                underline=font.get('underline', False),
                overstrike=font.get('overstrike', False)
            )

        kwargs = {
            'bd': kwargs.get('bd', json.get('bd', self.cget('bd'))),
            'font': font,
            'index': kwargs.get('index', json.get('index', self.next_index)),
            'tearoff': kwargs.get('tearoff', json.get('tearoff', 0)),
            'foreground': kwargs.get('foreground', json.get('foreground', self.cget('foreground'))),
            'background': kwargs.get('background', json.get('background', self.cget('background'))),
            'activeforeground': kwargs.get(
                'activeforeground', json.get('activeforeground', self.cget('activeforeground'))),
            'activebackground': kwargs.get(
                'activebackground', json.get('activebackground', self.cget('activebackground'))),
        }

        func = SubMenu if 'children' in json else MenuItem
        self.items[key] = func(self, json, **kwargs)

        if self.tearoff is None:
            self.tearoff = 0

        index = self.items[key].index
        if index is not None:
            for _, child in self.get_children.items():
                if child.index >= index:
                    child.index += 1
            self.items[key].index = index

    def config_children(self, **kwargs):

        def process(children):
            for index, child in children.items():
                if child.type == 'separator':
                    continue
                elif child.type == 'menu':
                    args = dict(kwargs)
                    args.pop('bd', None)
                    args.pop('relief', None)
                    child.config(**kwargs)
                    index = child.index - int(not self.tearoff)
                    self.entryconfig(index, **args)
                    process(child.get_children)
                else:
                    child.config(**kwargs)

        process(self.get_children)

    @property
    def next_index(self):
        self.__index += 1
        return self.__index

    @property
    def get_children(self):
        return self.items

    @property
    def has_children(self):
        return len(self.items)


class SubMenu(Menus):
    def __init__(self, parent, json, **kwargs):
        super().__init__(parent, **kwargs)

        self.type = 'menu'
        self.bd = kwargs.get('bd', json.get('bd'))
        self.font = kwargs.get('font', json.get('font'))
        self.label = kwargs.get('label', json.get('label'))
        self.image = kwargs.get('image', json.get('image'))
        self.index = kwargs.get('index', json.get('index'))
        self.state = kwargs.get('state', json.get('state'))
        self.relief = kwargs.get('relief', json.get('relief'))
        self.tearoff = kwargs.get('tearoff', json.get('tearoff'))
        self.compound = kwargs.get('compound', json.get('compound', 'left'))
        self.underline = kwargs.get('underline', json.get('underline'))
        self.foreground = kwargs.get('foreground', json.get('foreground'))
        self.background = kwargs.get('background', json.get('background'))
        self.activeforeground = kwargs.get('activeforeground', json.get('activeforeground'))
        self.activebackground = kwargs.get('activebackground', json.get('activebackground'))

        if not isinstance(parent, MenuBar):
            self.image = PhotoImage(file=path.join(getcwd(), 'tkmenus', 'images', 'blank-21x16.png'))

        kwargs = {
            'menu': self,
            'label': self.label,
            'image': self.image,
            'compound': self.compound,
            'underline': self.underline
        }
        if not self.index:
            parent.add_cascade(**kwargs)
        else:
            parent.insert_cascade(self.index, **kwargs)

        kwargs = {
            'font': self.font,
            'state': self.state,
            'foreground': self.foreground,
            'background': self.background,
            'activeforeground': self.activeforeground,
            'activebackground': self.activebackground,
        }

        for key, child in json.get('children').items():
            kwargs = {**kwargs, **{'index': self.next_index - int(not self.tearoff)}}

            if 'children' in child:
                self.items[key] = SubMenu(self, child, **{**kwargs, **{
                    'bd': child.get('bd', None),
                    'relief': child.get('relief', None),
                    'tearoff': child.get('tearoff', 0)
                }})
            else:
                self.items[key] = MenuItem(self, child, **kwargs)


class MenuBar(Menus):
    def __init__(self, parent, json, **kwargs):
        super().__init__(parent, **kwargs)
        self.populate(json.pop('children', None))
        print('-----------------------------------------------------------')
        print('System Platform (TkMenuBar)', self.platform)
        print('-----------------------------------------------------------')

        font = kwargs.get('font', json.get('font', None))
        self.font = None
        if font is not None:
            self.font = Font(**font)

        self.bd = kwargs.get('bd', json.get('bd', 0))
        self.relief = kwargs.get('relief', json.get('relief', 'flat'))
        self.tearoff = kwargs.get('tearoff', json.get('tearoff', 0))
        self.foreground = kwargs.get('foreground', json.get('foreground'))
        self.background = kwargs.get('background', json.get('background'))
        self.activeforeground = kwargs.get('activeforeground', json.get('activeforeground'))
        self.activebackground = kwargs.get('activebackground', json.get('activebackground'))

        self.config(
            bd=self.bd,
            font=self.font,
            relief=self.relief,
            tearoff=self.tearoff,
            foreground=self.foreground,
            background=self.background,
            activeforeground=self.activeforeground,
            activebackground=self.activebackground,
        )

        parent.config(menu=self)


class ContextMenu(Menus):
    def __init__(self, parent, json, **kwargs):
        super().__init__(parent, **kwargs)
        self.populate(json.pop('children', None))

        font = kwargs.get('font', json.get('font', None))
        self.font = None
        if font is not None:
            self.font = Font(**font)

        self.bd = kwargs.get('bd', json.get('bd', 0))
        self.relief = kwargs.get('relief', json.get('relief', 'flat'))
        self.tearoff = kwargs.get('tearoff', json.get('tearoff', 0))
        self.foreground = kwargs.get('foreground', json.get('foreground'))
        self.background = kwargs.get('background', json.get('background'))
        self.activeforeground = kwargs.get('activeforeground', json.get('activeforeground'))
        self.activebackground = kwargs.get('activebackground', json.get('activebackground'))

        self.config(
            bd=self.bd,
            font=self.font,
            relief=self.relief,
            tearoff=self.tearoff,
            foreground=self.foreground,
            background=self.background,
            activeforeground=self.activeforeground,
            activebackground=self.activebackground,
        )

        self.items = {}
        self.__leave = False
        self.__delay_destroy = 1000
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Escape>", self.on_escape)

    def on_enter(self, event):
        if event:
            self.__leave = False

    def on_leave(self, event):
        self.__leave = True

        def leave():
            if self.__leave:
                self.on_escape(event)

        self.after(self.__delay_destroy, leave)

    def on_escape(self, event):
        if event:
            self.unpost()
            self.__leave = False
