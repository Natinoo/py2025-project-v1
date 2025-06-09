from logger import Logger
from Sensory import TemperatureSensor, HumiditySensor, PressureSensor, LightSensor
from datetime import datetime, timedelta
from network.client import NetworkClient  # nowy import klienta sieciowego
import time

def main():
    # Tworzenie instancji loggera
    logger = Logger("config.json")
    logger.start()

    client = NetworkClient()
    
    # Tworzenie instancji czujników
    sensors = [
        TemperatureSensor("Temperatura", "Temperature Sensor", "°C", -10, 40),
        HumiditySensor("Wilgotność", "Humidity Sensor", "%", 0, 100),
        PressureSensor("Ciśnienie", "Pressure Sensor", "hPa", 950, 1050),
        LightSensor("Ilość światła", "Light Sensor", "lux", 0, 10000)
    ]

    try:
        # Run for 5 minutes
        end_time = datetime.now() + timedelta(minutes=5)
        while datetime.now() < end_time:
            for sensor in sensors:
                # Read sensor value
                value = sensor.read_value()
                timestamp = datetime.now()

                # Log locally
                logger.log_reading(sensor.sensor_id, timestamp, value, sensor.unit)

                # Send to server
                data = {
                    "sensor_id": sensor.sensor_id,
                    "value": value,
                    "unit": sensor.unit,
                    "timestamp": timestamp.isoformat()
                }
                client.send(data)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping sensor simulation...")
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
