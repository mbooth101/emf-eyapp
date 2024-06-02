import asyncio
import app
import random
import settings

from events.input import Buttons, BUTTON_TYPES


class EyApp(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.name = settings.get("name")

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.minimise()

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0,0,0).rectangle(-120,-120,240,240).fill()
        random.seed()
        greet = random.randrange(5)
        offset = random.randrange(25)
        offsety = random.randrange(10)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 0 + offsety).text("Ey Up")
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 0 + offsety).text("How Do")
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 0 + offsety).text("Now Then")
        if greet == 3:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 0 + offsety).text("Wotcha")
        if greet == 4:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 0 + offsety).text("Alreet")
        greet = random.randrange(3)
        offset = random.randrange(25)
        offsety = random.randrange(10)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 20 + offsety).text("Ahm " + self.name)
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 20 + offsety).text("I'm " + self.name)
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 20 + offsety).text("Me name is " + self.name)
        greet = random.randrange(4)
        offset = random.randrange(25)
        offsety = random.randrange(10)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 40 + offsety).text("Ow a tha?")
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 40 + offsety).text("Ah thee?")
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 40 + offsety).text("Orate?")
        if greet == 3:
            ctx.rgb(0.5,1,0).move_to(-80 + offset, 40 + offsety).text("Yareet?")
        ctx.restore()

__app_export__ = EyApp
