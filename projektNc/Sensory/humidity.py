import random
from datetime import datetime
from .base import Sensor

class HumiditySensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        temperature = random.uniform(15, 30)
        base_humidity = 80 - (temperature - 15) * 2
        fluctuation = random.uniform(-5, 5)
        value = min(max(self.min_value, base_humidity + fluctuation), self.max_value)
        self.last_value = value
        self.history.append((datetime.now(), value))
        return value
