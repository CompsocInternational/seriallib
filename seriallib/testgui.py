import tkinter
from typing import Callable

import seriallib.armcontroller

controller = seriallib.armcontroller.ArmController(
    "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_8513332303635140E1A0-if00"
)


def wrap(func: Callable) -> Callable:
    return func


root = tkinter.Tk()

grab_button = tkinter.Button(root, text="Grab", command=wrap(controller.grab))
grab_button.pack()

bin1_button = tkinter.Button(root, text="Bin 1", command=wrap(controller.move_bin1))
bin1_button.pack()

bin2_button = tkinter.Button(root, text="Bin 2", command=wrap(controller.move_bin2))
bin2_button.pack()

bin3_button = tkinter.Button(root, text="Bin 3", command=wrap(controller.move_bin3))
bin3_button.pack()

home_button = tkinter.Button(root, text="Home", command=wrap(controller.move_home))
home_button.pack()

root.mainloop()
