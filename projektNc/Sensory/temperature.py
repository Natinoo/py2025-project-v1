import math
import random
from datetime import datetime
from .base import Sensor

class TemperatureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour
        base_temp = 10 + 10 * math.sin(math.pi * hour / 24)
        noise = random.uniform(-2, 2)
        value = min(max(self.min_value, base_temp + noise), self.max_value)
        self.last_value = value
        self.history.append((datetime.now(), value))
        return value
