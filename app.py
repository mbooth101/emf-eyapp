import asyncio
import app
import random
import settings
import math

from events.input import Buttons, BUTTON_TYPES


# Display
display_x = 240
display_y = 240
display_height_inches = 1.28
ppi = display_x / display_height_inches

# Font size
one_pt = ppi / 72

class EyApp(app.App):

    def __init__(self):
        self.button_states = Buttons(self)
        self.name = settings.get("name")
        if not self.name:
            self.name = "<yobbo>"
        self.elapsed = 0
        self.accum = 0
        self.chaos = 5
        self.greet0 = 0
        self.greet1 = 0
        self.greet2 = 0
        self.level_font_size = 6 * one_pt

    def update(self, delta):
        self.elapsed = self.elapsed + (delta / (12 - self.chaos))
        self.accum = self.accum + delta
        delay = (12 - self.chaos) * 250
        if self.accum > delay:
            self.accum = self.accum - delay
            self.greet0 = random.randrange(7)
            self.greet1 = random.randrange(3)
            self.greet2 = random.randrange(3)
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

        x_factor = math.cos(math.radians(self.elapsed % 360)) * ratio
        y_factor = math.sin(math.radians(self.elapsed % 360)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = -10 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet0 == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ey Up")
        if self.greet0 == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("How Do")
        if self.greet0 == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Now Then")
        if self.greet0 == 3:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Wotcha")
        if self.greet0 == 4:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Alreet")
        if self.greet0 == 5:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Moornin")
        if self.greet0 == 6:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("G'day")

        x_factor = math.cos(math.radians((self.elapsed % 360) + 120)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 120)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 20 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet1 == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ahm " + self.name)
        if self.greet1 == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("I'm " + self.name)
        if self.greet1 == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Name's " + self.name)

        x_factor = math.cos(math.radians((self.elapsed % 360) + 240)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 240)) * ratio
        offset = -80 + (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 50 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet2 == 0:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ow a tha?")
        if self.greet2 == 1:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Ah thee?")
        if self.greet2 == 2:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Orate?")
        if self.greet2 == 3:
            ctx.rgb(0.5,1,0).move_to(offset, offsety).text("Yareet?")
        ctx.font_size = self.level_font_size
        ctx.rgb(1,1,1).move_to(-2, 100).text(str(self.chaos))
        ctx.restore()

__app_export__ = EyApp
