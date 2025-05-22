from logger import Logger
from Sensory import TemperatureSensor, HumiditySensor, PressureSensor, LightSensor
from datetime import datetime, timedelta
from network.client import NetworkClient  # nowy import klienta sieciowego
import time

def main():
    # Tworzenie instancji loggera
    logger = Logger("config.json")
    logger.start()

    client = NetworkClient(
        host="127.0.0.1",
        port=5000,
        timeout=5.0,
        retries=3
    )
    client.connect()
    
    # Tworzenie instancji czujników
    sensors = [
        TemperatureSensor("T1", "Temperature Sensor", "°C", -10, 40),
        HumiditySensor("H1", "Humidity Sensor", "%", 0, 100),
        PressureSensor("P1", "Pressure Sensor", "hPa", 950, 1050),
        LightSensor("L1", "Light Sensor", "lux", 0, 10000)
    ]

    # Symulacja pracy czujników
    end_time = datetime.now() + timedelta(minutes=5)
    while datetime.now() < end_time:
        for sensor in sensors:
            value = sensor.read_value()
            logger.log_reading(sensor.sensor_id, datetime.now(), value, sensor.unit)
            success = client.send({
                "sensor_id": sensor.sensor_id,
                "timestamp": datetime.now().isoformat(),
                "value": value,
                "unit": sensor.unit
            })
        time.sleep(1)

    # Zamykanie połączeń
    logger.stop()
    client.close()

if __name__ == "__main__":
    main()
