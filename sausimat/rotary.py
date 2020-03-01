import RPi.GPIO as GPIO
import time
import asyncio

class Rotary:
    def __init__(self, pin_a_board, pin_b_board, initial_value=0):
        self.in_a = pin_a_board
        self.in_b = pin_b_board

        # Merker fuer Encoder-Zustand (global)
        self.old_a = 1
        self.old_b = 1

        self.counter = initial_value

        # Pullup-Widerstand einschalten
        GPIO.setup(self.in_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.in_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_encoder(self):
      # liest den Encoder aus. Falls die Werte der Eingangspins
      # alten Wert abweichen, Richtung detektieren.
      # Rueckgabewert: -1, 0, +1
      result = 0

      # GPIO-Pins einlesen
      new_a = GPIO.input(self.in_a)
      new_b = GPIO.input(self.in_b)

      # Falls sich etwas geaendert hat, Richtung feststellen
      if (new_a != self.old_a or new_b != self.old_b):
        if (self.old_a == 0 and new_a == 1):
          result = (self.old_b * 2 - 1)
        elif (self.old_b == 0 and new_b == 1):
          result = -(self.old_a * 2 - 1)
      self.old_a = new_a
      self.old_b = new_b
      # entprellen
      time.sleep(0.02)
      return result

    async def run(self, callback=None):
        print('Start checking rotary')
        while True:
          change = self.get_encoder()
          if change != 0:
            self.counter = self.counter + change
            callback(self.counter)
          await asyncio.sleep(0.1)