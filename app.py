import asyncio
import app
import random
import settings
import math

from events.input import Buttons, BUTTON_TYPES


class EyApp(app.App):

    def __init__(self):
        self.button_states = Buttons(self)
        self.name = settings.get("name")
        if not self.name:
            self.name = "<yobbo>"
        self.elapsed = 0
        self.chaos = 5

    def update(self, delta):
        self.elapsed = self.elapsed + (delta / (12 - self.chaos))
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.minimise()
        if self.button_states.get(BUTTON_TYPES["UP"]):
            if self.chaos < 11:
                self.chaos = self.chaos + 1
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            if self.chaos > 0:
                self.chaos = self.chaos - 1

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0,0,0).rectangle(-120,-120,240,240).fill()
        random.seed()
        ratio = self.chaos / 12
        greet = random.randrange(5)
        x_factor = math.cos(math.radians(self.elapsed % 360)) * ratio
        y_factor = math.sin(math.radians(self.elapsed % 360)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = -10 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ey Up")
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("How Do")
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Now Then")
        if greet == 3:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Wotcha")
        if greet == 4:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Alreet")
        greet = random.randrange(3)
        x_factor = math.cos(math.radians((self.elapsed % 360) + 120)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 120)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 20 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ahm " + self.name)
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("I'm " + self.name)
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Me name is " + self.name)
        greet = random.randrange(4)
        x_factor = math.cos(math.radians((self.elapsed % 360) + 240)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 240)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 50 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ow a tha?")
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ah thee?")
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Orate?")
        if greet == 3:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Yareet?")
        ctx.rgb(1,1,1).move_to(-10, 100).text(self.chaos)
        ctx.restore()

__app_export__ = EyApp
