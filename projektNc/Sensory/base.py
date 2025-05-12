import random
from datetime import datetime

class Sensor:
    def __init__(self, sensor_id, name, unit, min_value, max_value, frequency=1):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency
        self.active = True
        self.last_value = None
        self.history = []
        self._callbacks = []

    def read_value(self):
        raise NotImplementedError("Metoda musi być nadpisana w klasie potomnej.")

    def calibrate(self, calibration_factor):
        if self.last_value is None:
            self.read_value()
        self.last_value *= calibration_factor
        return self.last_value

    def get_last_value(self):
        if self.last_value is None:
            return self.read_value()
        return self.last_value

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def register_callback(self, callback):
        self._callbacks.append(callback)

    def notify_callbacks(self):
        timestamp = datetime.now()
        value = self.read_value()
        for callback in self._callbacks:
            callback(self.sensor_id, timestamp, value, self.unit)

    def __str__(self):
        return f"{self.name} ({self.sensor_id}): {self.last_value} {self.unit}"

    def read_value(self):
        raise NotImplementedError("Metoda musi być nadpisana w klasie potomnej.")

        # Po implementacji w klasie potomnej, ta część będzie wykonana:
        self.notify_callbacks()
        return self.last_value
