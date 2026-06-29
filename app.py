import asyncio
import app
import random
import settings
import math
import time

from app_components.background import Background as bg
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import *
from system.scheduler.events import *

from micropython import const

# Display
display_x = const(240)
display_y = const(240)
display_height_inches = const(1.28)
ppi = display_x / display_height_inches

# Font size
one_pt = ppi / 72

greetings = [
    [
        "Ey Up",
        "How Do",
        "Now Then",
        "Wotcha",
        "Alreet",
        "G'day",
        "Ar kid",
        "<T>",
        "Tha Reet",
    ], [
        "<N> innit",
        "Ahm <N>",
        "I'm <N>",
        "Name's <N>",
        "<N> 'ere",
        "It's <N>",
    ], [
        "Ow a tha?",
        "Ah thee?",
        "Orate?",
        "Yareet?",
        "Fettlin well?",
        "Ow's tha deein?",
        "Put kettle on",
        "Tha mashin?",
        "Get mashin",
        "Went a brew?",
        "Gerron wi yer",
        "Wot's fer tea?",
        "Wekkin 'ard?",
        "Gan tut pub?",
    ]
]

class EyApp(app.App):

    def __init__(self):
        random.seed()
        self.button_states = Buttons(self)
        self.name = settings.get("name")
        if not self.name:
            self.name = "Yobbo"
        self.brightness = settings.get("pattern_brightness")
        if not self.brightness:
            self.brightness = 0.1
        self.elapsed = 0
        self.text_accum = [0,0,0]
        self.chaos = self._load()
        self._update_chaos(0)
        self.col_hue = 0
        self.led_hue = 127
        self.col = EyApp.hsl_to_rgb(self.col_hue, 255, 255)
        self.led = EyApp.hsl_to_rgb(self.led_hue, 191, int(255 * self.brightness), False)
        self.greets = [0,0,0]
        self.main_font_size = 14
        self.level_font_size = 5

        self.highlight_active = False
        self.highlight_counter = 3 * max(1, 12 - self.chaos)

        self.show_perf = False
        self.current_time = 0
        self.last_time = 0
        self.perf_idx = 0
        self.fps_samples = [0,0,0,0,0]
        self.frame_time_samples = [0,0,0,0,0]
        self.fps_avg = 0
        self.frame_time_avg = 0

        # Attempt to set RTC to correct time
        try:
            import ntptime
            ntptime.settime()
        except Exception as e:
            pass

        eventbus.on_async(RequestForegroundPushEvent, self._resume, self)
        eventbus.on_async(RequestForegroundPopEvent, self._pause, self)
        eventbus.emit(PatternDisable())

    def _load(self):
        try:
            with open('/eyapp.data', 'r') as f:
                chaos = int(next(f))
        except:
            chaos = 5
        if chaos is None:
            chaos = 5
        return chaos

    def _save(self):
        try:
            with open('/eyapp.data', 'w') as f:
                f.write('{}'.format(str(self.chaos)))
        except:
            pass

    async def _resume(self, event: RequestForegroundPushEvent):
        # Disable firmware led pattern
        eventbus.emit(PatternDisable())

        # Settings might have changed while we've been paused
        self.name = settings.get("name")
        if not self.name:
            self.name = "Yobbo"
        self.brightness = settings.get("pattern_brightness")
        if not self.brightness:
            self.brightness = 0.1

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
        bg.update(delta)
        self.elapsed = self.elapsed + (delta / (12 - self.chaos))

        # Choose new greetings
        self.text_accum = [x + delta for x in self.text_accum]
        for idx in range(len(self.text_accum)):
            accum = self.text_accum[idx]
            delay = self.text_delay + 25 * idx
            if accum <= delay:
                continue

            self.text_accum[idx] = accum - delay
            if self.chaos <= 0:
                continue

            self.greets[idx] = random.randrange(len(greetings[idx]))
            if idx != 1:
                continue

            self.highlight_counter -= 1
            if self.highlight_counter <= 0:
                x_val = max(1, 12 - self.chaos)
                self.highlight_active = not self.highlight_active
                self.highlight_counter = x_val if self.highlight_active else 3 * x_val

        # Choose new text colour
        if self.chaos > 0:
            col_inc = (delta / 1000) * self.col_speed
            self.col_hue = (self.col_hue + col_inc) % 255
        else:
            self.highlight_active = False

        # Choose new led colour
        if self.chaos > 0:
            led_inc = (delta / 1000) * self.led_speed
            self.led_hue = (self.led_hue - led_inc)
            if (self.led_hue < 0):
                self.led_hue = self.led_hue + 255
            self.led = EyApp.hsl_to_rgb(math.floor(self.led_hue), 191, int(255 * self.brightness), False)

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
            self.button_states.clear()

        # Decrease chaos
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            self._update_chaos(-1)
            self.button_states.clear()

        # Show framerate
        if self.button_states.get(BUTTON_TYPES["RIGHT"]):
            self.show_perf = True
        else:
            self.show_perf = False

        # Choose new greeting text size
        self.main_font_size = 14 + (random.randrange(self.chaos + 1) / 2)

    def _update_chaos(self, direction):
        self.chaos = max(0, min(self.chaos + 1 * direction, 11))
        self.text_delay = (12 - self.chaos) * 350
        self.col_speed = self.chaos ** 2
        self.led_speed = self.chaos ** 3
        self._save()

    def draw(self, ctx):
        # Calculate time since last frame
        self.current_time = time.ticks_us()
        frame_time = time.ticks_diff(self.current_time, self.last_time)
        self.last_time = self.current_time

        # Calculate perf metrics
        self.frame_time_samples[self.perf_idx] = frame_time
        self.fps_samples[self.perf_idx] = 1_000_000 / frame_time
        self.perf_idx = self.perf_idx + 1
        if self.perf_idx > 4:
            self.perf_idx = 0
            self.frame_time_avg = int(sum(self.frame_time_samples) / 5)
            self.fps_avg = sum(self.fps_samples) / 5

        bg.draw(ctx)

        ctx.text_align = ctx.CENTER
        ratio = self.chaos / 12

        ctx.font_size = self.main_font_size * one_pt

        t = time.localtime()[3];
        time_greet = "Eeevenin"
        if t >= 0 and t < 12:
            time_greet = "Mooornin"
        if t >= 12 and t < 17:
            time_greet = "Aaafternoon"

        x_factor = math.cos(math.radians(self.elapsed % 360)) * ratio
        y_factor = math.sin(math.radians(self.elapsed % 360)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = -20 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        start_greet = greetings[0][self.greets[0]].replace("<T>", time_greet)
        ctx.rgb(*self.col).move_to(offset, offsety).text(start_greet)

        x_factor = math.cos(math.radians((self.elapsed % 360) + 120)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 120)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 10 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        greeting_tmpl = greetings[1][self.greets[1]]
        opposite_hue = (self.col_hue + 128) % 255
        opposite_col = EyApp.hsl_to_rgb(math.floor(opposite_hue), 255, 255)

        if "<N>" in greeting_tmpl:
            part_before, part_after = greeting_tmpl.split("<N>", 1)
            w_before = ctx.text_width(part_before)
            w_name = ctx.text_width(self.name)
            w_after = ctx.text_width(part_after)
            total_width = w_before + w_name + w_after

            start_x = offset - total_width / 2

            name_col = opposite_col if self.highlight_active else self.col
            ctx.text_align = ctx.LEFT
            ctx.rgb(*self.col).move_to(start_x, offsety).text(part_before)
            ctx.rgb(*name_col).move_to(start_x + w_before, offsety).text(self.name)
            ctx.rgb(*self.col).move_to(start_x + w_before + w_name, offsety).text(part_after)
            ctx.text_align = ctx.CENTER
        else:
            intro_greet = greeting_tmpl.replace("<N>", self.name)
            ctx.rgb(*self.col).move_to(offset, offsety).text(intro_greet)

        x_factor = math.cos(math.radians((self.elapsed % 360) + 240)) * ratio
        y_factor = math.sin(math.radians((self.elapsed % 360) + 240)) * ratio
        offset = (20 * x_factor) + random.randrange(1 + 2 * self.chaos)
        offsety = 40 + (5 * y_factor) + random.randrange(1 + 1 * self.chaos)
        end_greet = greetings[2][self.greets[2]].replace("<T>", time_greet)
        ctx.rgb(*self.col).move_to(offset, offsety).text(end_greet)

        ctx.font_size = self.level_font_size * one_pt
        ctx.rgb(1, 1, 1).move_to(0, 100).text(str(self.chaos))
        if self.chaos > 0:
            ctx.move_to(-5, 105).line_to(0, 110).line_to(5, 105).line_to(-5, 105).fill()
        if self.chaos < 11:
            ctx.move_to(-5, 85).line_to(0, 80).line_to(5, 85).line_to(-5, 85).fill()

        if self.show_perf:
            ctx.rgb(1, 1, 1).move_to(0, -80).text(f"{self.fps_avg:.2f} fps")
            ctx.rgb(1, 1, 1).move_to(0, -60).text(f"{self.frame_time_avg} us")
        for i in range(12):
            tildagonos.leds[i+1] = self.led
        tildagonos.leds.write()


__app_export__ = EyApp
