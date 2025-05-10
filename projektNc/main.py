from logger import Logger
from Sensory import TemperatureSensor, HumiditySensor, PressureSensor, LightSensor
from datetime import datetime

def main():
    # Tworzenie instancji loggera na podstawie pliku konfiguracyjnego
    logger = Logger("config.json")
    logger.start()

    # Tworzenie instancji czujników
    temp_sensor = TemperatureSensor("T1", "Temperature Sensor", "°C", -10, 40)
    humidity_sensor = HumiditySensor("H1", "Humidity Sensor", "%", 0, 100)

    # Generowanie danych i logowanie
    for _ in range(100):
        temp_value = temp_sensor.read_value()
        humidity_value = humidity_sensor.read_value()

        # Logowanie danych do pliku
        logger.log_reading(temp_sensor.sensor_id, datetime.now(), temp_value, "°C")
        logger.log_reading(humidity_sensor.sensor_id, datetime.now(), humidity_value, "%")


    # Zamykanie logera
    logger.stop()

if __name__ == "__main__":
    main()
