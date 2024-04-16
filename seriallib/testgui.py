import tkinter as tk
import asyncio
from typing import Any, Callable, Coroutine

import seriallib.armcontroller

controller = seriallib.armcontroller.ArmController(
    "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_8513332303635140E1A0-if00"
)


def wrap(func: Callable[[], Coroutine[Any,Any,None]]) -> Callable:
    def wrapper():
        asyncio.create_task(func())

    return wrapper


class App(tk.Tk):
    
    def __init__(self, loop, interval=1/60):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.tasks.append(loop.create_task(self.setup()))
        self.tasks.append(loop.create_task(self.updater(interval)))

    async def setup(self):
        grab_button = tk.Button(self, text="Grab", command=wrap(controller.grab))
        grab_button.pack()

        bin1_button = tk.Button(self, text="Bin 1", command=wrap(controller.move_bin1))
        bin1_button.pack()

        bin2_button = tk.Button(self, text="Bin 2", command=wrap(controller.move_bin2))
        bin2_button.pack()

        bin3_button = tk.Button(self, text="Bin 3", command=wrap(controller.move_bin3))
        bin3_button.pack()

        neutral_button = tk.Button(self, text="Neutral", command=wrap(controller.move_neutral))
        neutral_button.pack()
        
        self.loop
        

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


loop = asyncio.get_event_loop()
app = App(loop)
loop.run_forever()
loop.close()