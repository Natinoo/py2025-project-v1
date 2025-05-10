import math
import random
from datetime import datetime
from .base import Sensor

class LightSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour
        if 6 <= hour <= 18:
            base_light = 10000 * math.sin(math.pi * (hour - 6) / 12)
        else:
            base_light = 0
        fluctuation = random.uniform(-500, 500)
        value = min(max(self.min_value, base_light + fluctuation), self.max_value)
        self.last_value = value
        self.history.append((datetime.now(), value))
        return value
