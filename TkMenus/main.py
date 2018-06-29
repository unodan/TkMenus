########################################################################################################################
#    File: main.py
#  Author: Dan Huckson, https://github.com/unodan
#    Date: 2018-06-29
########################################################################################################################
from os import path, getcwd, remove
from json import load, dump
from tkinter import Tk, messagebox
from tkmenus import MenuBar


def menu_exit():
    exit(0)


def menu_open():
    messagebox.showinfo('Info', 'Open menu item was selected.')


class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('TkMenuBar Demo Program')
        self.geometry('600x400')
        self.protocol('WM_DELETE_WINDOW', menu_exit)

        config = path.join(getcwd(), 'tkmenus', 'config.json')

        # Delete this after debugging.
        if path.isfile(config):
            remove(config)

        if path.isfile(config):
            with open(config, "r") as file:
                menus = load(file)
        else:
            # Border types "flat", "raised", "sunken", "ridge", "solid", "groove"
            menus = {
                'bd': 0,
                'children': {
                    'game': {
                        'label': 'Game',
                        'underline': 0,
                        'children': {
                            'open': {
                                'label': 'Open',
                                'accelerator': 'Alt+O',
                                'command': 'main.menu_open',
                            },
                        },
                    },
                },
            }

            with open(config, "w") as file:
                dump(menus, file, indent=4)

        mb = self.menubar = MenuBar(self, menus)

        mb.config_children(
            bd=2,
            relief='ridge',
        )


def main():
    App().mainloop()


if __name__ == '__main__':
    main()
