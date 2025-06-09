import os
import csv
import json
import zipfile
import shutil
from datetime import datetime, timedelta
from typing import Optional, Iterator, Dict


class Logger:
    def __init__(self, config_path: str):
        """
        Inicjalizuje logger na podstawie pliku JSON.
        :param config_path: Ścieżka do pliku konfiguracyjnego (.json)
        """
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.log_dir = config["log_dir"]
        self.filename_pattern = config["filename_pattern"]
        self.buffer_size = config["buffer_size"]
        self.rotate_every_hours = config["rotate_every_hours"]
        self.max_size_mb = config["max_size_mb"]
        self.rotate_after_lines = config["rotate_after_lines"]
        self.retention_days = config["retention_days"]

        # Inicjalizacja katalogów
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, 'archive'), exist_ok=True)

        self.buffer = []
        self.current_file = None
        self.current_file_path = None
        self.current_file_size = 0
        self.current_line_count = 0

    def _get_filename(self) -> str:
        """
        Zwraca nazwę pliku na podstawie wzorca.
        """
        return os.path.join(self.log_dir, datetime.now().strftime(self.filename_pattern))

    def start(self) -> None:
        """
        Otwiera nowy plik CSV do logowania. Jeśli plik jest nowy, zapisuje nagłówek.
        """
        self.current_file_path = self._get_filename()
        if not os.path.exists(self.current_file_path):
            with open(self.current_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'sensor_id', 'value', 'unit'])
        self.current_file = open(self.current_file_path, 'a', newline='')
        self.current_file_size = os.path.getsize(self.current_file_path)
        self.current_line_count = sum(1 for _ in open(self.current_file_path))  # Liczenie linii

    def stop(self) -> None:
        """
        Wymusza zapis bufora i zamyka bieżący plik.
        """
        if self.current_file:
            self._flush_buffer()
            self.current_file.close()
            self.current_file = None

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str) -> None:
        """
        Dodaje wpis do bufora i ewentualnie wykonuje rotację pliku.
        """
        self.buffer.append([timestamp, sensor_id, value, unit])

        # Jeżeli bufor jest pełny, zapisujemy dane i wykonujemy rotację
        if len(self.buffer) >= self.buffer_size:
            self._flush_buffer()
            self._check_rotation()

    def _flush_buffer(self) -> None:
        """
        Zapisuje dane z bufora do pliku.
        """
        if self.current_file:
            writer = csv.writer(self.current_file)
            writer.writerows(self.buffer)
            self.buffer.clear()

    def _check_rotation(self) -> None:
        """
        Sprawdza, czy należy przeprowadzić rotację pliku.
        """
        if self._needs_rotation():
            self.stop()  # Zakończenie bieżącego pliku
            self._rotate()

    def _needs_rotation(self) -> bool:
        """
        Sprawdza, czy plik wymaga rotacji na podstawie rozmiaru, liczby linii lub czasu.
        """
        if self.current_file_size >= self.max_size_mb * 1024 * 1024:  # Przekroczenie rozmiaru pliku
            return True
        if self.current_line_count >= self.rotate_after_lines:  # Przekroczenie liczby linii
            return True
        # Opcjonalnie: Przekroczenie interwału czasu (nie zaimplementowane w tej wersji)
        return False

    def _rotate(self) -> None:
        """
        Wykonuje rotację pliku: zamyka bieżący plik, przenosi go do archiwum.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = os.path.join(self.log_dir, 'archive', f"{timestamp}_{os.path.basename(self.current_file_path)}")

        # Przenoszenie do archiwum i kompresja
        shutil.move(self.current_file_path, archive_path)
        self._compress_archive(archive_path)

        # Usuwanie archiwów starszych niż retention_days
        self._clean_old_archives()

        self.start()  # Rozpoczęcie nowego pliku

    def _compress_archive(self, archive_path: str) -> None:
        """
        Kompresuje plik logu do formatu ZIP.
        """
        zip_path = f"{archive_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(archive_path, os.path.basename(archive_path))
        os.remove(archive_path)  # Usunięcie oryginalnego pliku po kompresji

    def _clean_old_archives(self) -> None:
        """
        Usuwa archiwa starsze niż retention_days.
        """
        now = datetime.now()
        archive_dir = os.path.join(self.log_dir, 'archive')
        for filename in os.listdir(archive_dir):
            file_path = os.path.join(archive_dir, filename)
            if os.path.getmtime(file_path) < (now - timedelta(days=self.retention_days)).timestamp():
                os.remove(file_path)

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        """
        Pobiera wpisy z logów zadanego zakresu i opcjonalnie konkretnego czujnika.
        """
        for root, dirs, files in os.walk(self.log_dir):
            for file in files:
                if file.endswith('.csv'):
                    with open(os.path.join(root, file), 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                            if start <= timestamp <= end:
                                if sensor_id is None or row['sensor_id'] == sensor_id:
                                    yield row

    def _needs_rotation(self) -> bool:
        """Sprawdza, czy plik wymaga rotacji."""
        if self.current_file_size >= self.max_size_mb * 1024 * 1024:
            return True
        if self.current_line_count >= self.rotate_after_lines:
            return True
        # Sprawdzenie rotacji czasowej
        if hasattr(self, 'last_rotation_time'):
            if (datetime.now() - self.last_rotation_time) >= timedelta(hours=self.rotate_every_hours):
                return True
        else:
            self.last_rotation_time = datetime.now()
        return False

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        """Pobiera wpisy z logów zadanego zakresu."""
        for root, dirs, files in os.walk(self.log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.csv') or file.endswith('.zip'):
                    with (zipfile.ZipFile(file_path, 'r') if file.endswith('.zip')
                    else open(file_path, 'r')) as f:
                        if file.endswith('.zip'):
                            with f.open(f.namelist()[0]) as csvfile:
                                reader = csv.DictReader(line.decode('utf-8') for line in csvfile)
                        else:
                            reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S.%f'
                                if '.' in row['timestamp']
                                else '%Y-%m-%d %H:%M:%S')
                                if start <= timestamp <= end:
                                    if sensor_id is None or row['sensor_id'] == sensor_id:
                                        yield row
                            except ValueError as e:
                                print(f"Błąd parsowania wiersza: {row}, błąd: {e}")