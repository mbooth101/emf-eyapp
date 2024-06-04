import asyncio
import app
import random
import settings
import math
import time

from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import *
from system.scheduler.events import *

# Display
display_x = 240
display_y = 240
display_height_inches = 1.28
ppi = display_x / display_height_inches

# Font size
one_pt = ppi / 72

class EyApp(app.App):

    def __init__(self):
        random.seed()
        self.button_states = Buttons(self)
        self.name = settings.get("name")
        if not self.name:
            self.name = "<yobbo>"
        self.elapsed = 0
        self.text_accum = 0
        self.col_accum = 0
        self.chaos = 5
        self.text_delay = (12 - self.chaos) * 350
        self.col_delay = (12 - self.chaos) * 500
        self.col_hue = 0
        self.col = EyApp.hsl_to_rgb(self.col_hue, 255, 255)
        self.greet0 = 0
        self.greet1 = 0
        self.greet2 = 0
        self.main_font_size = 14
        self.level_font_size = 6
        eventbus.on_async(RequestForegroundPushEvent, self._resume, self)
        eventbus.on_async(RequestForegroundPopEvent, self._pause, self)
        eventbus.emit(PatternDisable())

    async def _resume(self, event: RequestForegroundPushEvent):
        # Disable firmware led pattern
        eventbus.emit(PatternDisable())

    async def _pause(self, event: RequestForegroundPopEvent):
        # Renable firmware led pattern when we minimise
        eventbus.emit(PatternEnable())

    @staticmethod
    def hsl_to_rgb(h, s, v):
        # Returns rgb normalised to between 0 and 1
        if s == 0:
            return (v / 255, v / 255, v / 255)
        region = h // 43
        remainder = (h - (region * 43)) * 6
        a = (v * (255 - s)) >> 8
        b = (v * (255 - ((s * remainder) >> 8))) >> 8
        c = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8
        if region == 0:
            return (v / 255, c / 255, a / 255)
        if region == 1:
            return (b / 255, v / 255, a / 255)
        if region == 2:
            return (a / 255, v / 255, c / 255)
        if region == 3:
            return (a / 255, b / 255, v / 255)
        if region == 4:
            return (c / 255, a / 255, v / 255)
        if region == 5:
            return (v / 255, a / 255, b / 255)
        return None

    def update(self, delta):
        self.elapsed = self.elapsed + (delta / (12 - self.chaos))

        # Choose new greetings
        self.text_accum = self.text_accum + delta
        if self.text_accum > self.text_delay:
            self.text_accum = self.text_accum - self.text_delay
            self.greet0 = random.randrange(7)
            self.greet1 = random.randrange(4)
            self.greet2 = random.randrange(3)

        # Choose new text colour
        self.col_accum = self.col_accum + delta
        if self.col_accum > self.col_delay:
            self.col_accum = self.col_accum - self.col_delay
            self.col_hue = (self.col_hue + 158) % 255
            self.col = EyApp.hsl_to_rgb(self.col_hue, 255, 255)

        # Exit the app
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

        # Increase chaos
        if self.button_states.get(BUTTON_TYPES["UP"]):
            if self.chaos < 11:
                self.chaos = self.chaos + 1
            self.text_delay = (12 - self.chaos) * 350
            self.col_delay = (12 - self.chaos) * 500

        # Decrease chaos
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            if self.chaos > 0:
                self.chaos = self.chaos - 1
            self.text_delay = (12 - self.chaos) * 350
            self.col_delay = (12 - self.chaos) * 500

        # Choose new greeting text size
        self.main_font_size = 14 + (random.randrange(self.chaos + 1) / 2)

    def draw(self, ctx):
        ctx.save()
        ctx.text_align = ctx.CENTER
        ctx.rgb(0,0,0).rectangle(-120,-120,240,240).fill()
        ratio = self.chaos / 12

        ctx.font_size = self.main_font_size * one_pt

        x_factor = math.cos(math.radians(self.elapsed % 360)) * ratio
        y_factor = math.sin(math.radians(self.elapsed % 360)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = -10 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet0 == 0:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Ey Up")
        if self.greet0 == 1:
            ctx.rgb(*self.col).move_to(offset, offsety).text("How Do")
        if self.greet0 == 2:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Now Then")
        if self.greet0 == 3:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Wotcha")
        if self.greet0 == 4:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Alreet")
        if self.greet0 == 5:
            t = time.localtime()[3];
            if t >= 0 and t < 12:
                ctx.rgb(*self.col).move_to(offset, offsety).text("Mooornin")
            if t >= 12 and t < 17:
                ctx.rgb(*self.col).move_to(offset, offsety).text("Aaafternoon")
            if t >= 17:
                ctx.rgb(*self.col).move_to(offset, offsety).text("Eeevenin")
        if self.greet0 == 6:
            ctx.rgb(*self.col).move_to(offset, offsety).text("G'day")

        x_factor = math.cos(math.radians((self.elapsed % 360) + 120)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 120)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 20 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet1 == 0:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Ahm " + self.name)
        if self.greet1 == 1:
            ctx.rgb(*self.col).move_to(offset, offsety).text("I'm " + self.name)
        if self.greet1 == 2:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Name's " + self.name)
        if self.greet1 == 3:
            ctx.rgb(*self.col).move_to(offset, offsety).text(self.name + " 'ere")

        x_factor = math.cos(math.radians((self.elapsed % 360) + 240)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 240)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 50 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        if self.greet2 == 0:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Ow a tha?")
        if self.greet2 == 1:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Ah thee?")
        if self.greet2 == 2:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Orate?")
        if self.greet2 == 3:
            ctx.rgb(*self.col).move_to(offset, offsety).text("Yareet?")

        ctx.font_size = self.level_font_size * one_pt
        ctx.rgb(1, 1, 1).move_to(0, 100).text(str(self.chaos))
        ctx.restore()

__app_export__ = EyApp
