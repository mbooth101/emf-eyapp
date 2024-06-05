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
        self.chaos = 5
        self._update_chaos(0)
        self.col_hue = 0
        self.led_hue = 127
        self.col = EyApp.hsl_to_rgb(self.col_hue, 255, 255)
        self.led = EyApp.hsl_to_rgb(self.led_hue, 191, 3, False)
        self.greet0 = 0
        self.greet1 = 0
        self.greet2 = 0
        self.main_font_size = 14
        self.level_font_size = 6

        # Attempt to set RTC to correct time
        try:
            import ntptime
            ntptime.settime()
        except Exception as e:
            pass

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
    def hsl_to_rgb(h, s, v, norm=True):
        rgb = (0, 0, 0)
        if s == 0:
            rgb = (v, v, v)
        region = h // 43
        remainder = (h - (region * 43)) * 6
        a = (v * (255 - s)) >> 8
        b = (v * (255 - ((s * remainder) >> 8))) >> 8
        c = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8
        if region == 0:
            rgb = (v, c, a)
        if region == 1:
            rgb = (b, v, a)
        if region == 2:
            rgb = (a, v, c)
        if region == 3:
            rgb = (a, b, v)
        if region == 4:
            rgb = (c, a, v)
        if region == 5:
            rgb = (v, a, b)
        # Optionally returns rgb normalised to between 0 and 1
        if norm:
            r, g, b = map(lambda x: x / 255, rgb)
            return (r, g, b)
        return rgb

    def update(self, delta):
        self.elapsed = self.elapsed + (delta / (12 - self.chaos))

        # Choose new greetings
        self.text_accum = self.text_accum + delta
        if self.text_accum > self.text_delay:
            self.text_accum = self.text_accum - self.text_delay
            if self.chaos > 0:
                self.greet0 = random.randrange(7)
                self.greet1 = random.randrange(4)
                self.greet2 = random.randrange(4)

        # Choose new text colour
        if self.chaos > 0:
            col_inc = (delta / 1000) * self.col_speed
            self.col_hue = (self.col_hue + col_inc) % 255
            self.col = EyApp.hsl_to_rgb(math.floor(self.col_hue), 255, 255)

        # Choose new led colour
        if self.chaos > 0:
            led_inc = (delta / 1000) * self.led_speed
            self.led_hue = (self.led_hue - led_inc)
            if (self.led_hue < 0):
                self.led_hue = self.led_hue + 255
            self.led = EyApp.hsl_to_rgb(math.floor(self.led_hue), 191, 3, False)

        # Exit the app
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

        # Increase chaos
        if self.button_states.get(BUTTON_TYPES["UP"]):
            self._update_chaos(1)

        # Decrease chaos
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            self._update_chaos(-1)

        # Choose new greeting text size
        self.main_font_size = 14 + (random.randrange(self.chaos + 1) / 2)

    def _update_chaos(self, direction):
        if direction > 0 and self.chaos < 11:
            self.chaos = self.chaos + 1
        if direction < 0 and self.chaos > 0:
            self.chaos = self.chaos - 1
        self.text_delay = (12 - self.chaos) * 350
        self.col_speed = self.chaos ** 2
        self.led_speed = self.chaos ** 3

    def draw(self, ctx):
        ctx.save()
        ctx.text_align = ctx.CENTER
        ctx.rgb(0,0,0).rectangle(-120,-120,240,240).fill()
        ratio = self.chaos / 12

        ctx.font_size = self.main_font_size * one_pt

        x_factor = math.cos(math.radians(self.elapsed % 360)) * ratio
        y_factor = math.sin(math.radians(self.elapsed % 360)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = -20 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
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
        offsety = 10 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
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
        offsety = 40 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
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
        if self.chaos > 0:
            ctx.move_to(-5, 105).line_to(0, 110).line_to(5, 105).line_to(-5, 105).fill()
        if self.chaos < 11:
            ctx.move_to(-5, 85).line_to(0, 80).line_to(5, 85).line_to(-5, 85).fill()
        ctx.restore()

        for i in range(12):
            tildagonos.leds[i+1] = self.led


__app_export__ = EyApp
