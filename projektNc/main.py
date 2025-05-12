from logger import Logger
from Sensory import TemperatureSensor, HumiditySensor, PressureSensor, LightSensor
from datetime import datetime, timedelta
import time

def main():
    # Tworzenie instancji loggera
    logger = Logger("config.json")
    logger.start()

    # Tworzenie instancji czujników
    sensors = [
        TemperatureSensor("T1", "Temperature Sensor", "°C", -10, 40),
        HumiditySensor("H1", "Humidity Sensor", "%", 0, 100),
        PressureSensor("P1", "Pressure Sensor", "hPa", 950, 1050),
        LightSensor("L1", "Light Sensor", "lux", 0, 10000)
    ]

    # Rejestracja callbacków
    for sensor in sensors:
        sensor.register_callback(logger.log_reading)

    # Symulacja pracy czujników
    end_time = datetime.now() + timedelta(minutes=5)
    while datetime.now() < end_time:
        for sensor in sensors:
            sensor.notify_callbacks()
        time.sleep(1)  # Odczyt co 1 sekundę

    # Zamykanie logera
    logger.stop()

    # Przykład odczytu logów
    print("\nOstatnie odczyty:")
    start_time = datetime.now() - timedelta(minutes=1)
    for log in logger.read_logs(start_time, datetime.now()):
        print(f"{log['timestamp']} - {log['sensor_id']}: {log['value']} {log['unit']}")

if __name__ == "__main__":
    main()
