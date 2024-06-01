import asyncio
import app
import random

from events.input import Buttons, BUTTON_TYPES


class EyApp(app.App):
    def __init__(self):
        self.button_states = Buttons(self)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.minimise()

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0,0,0).rectangle(-120,-120,240,240).fill()
        random.seed()
        greet = random.randrange(5)
        if greet == 0:
            ctx.rgb(0.5,1,0).move_to(-80,0).text("Ey Up")
        if greet == 1:
            ctx.rgb(0.5,1,0).move_to(-80,0).text("How Do")
        if greet == 2:
            ctx.rgb(0.5,1,0).move_to(-80,0).text("Now Then")
        if greet == 3:
            ctx.rgb(0.5,1,0).move_to(-80,0).text("Wotcha")
        if greet == 4:
            ctx.rgb(0.5,1,0).move_to(-80,0).text("Alreet")
        ctx.restore()

__app_export__ = EyApp
