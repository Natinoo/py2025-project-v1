import random
from datetime import datetime
from .base import Sensor

class PressureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        fluctuation = random.gauss(0, 1.5)
        base_pressure = 1013.25 + fluctuation
        value = min(max(self.min_value, base_pressure), self.max_value)
        self.last_value = value
        self.history.append((datetime.now(), value))
        return value
