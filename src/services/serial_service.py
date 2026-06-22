import serial
import re
import time

from config.settings import SERIAL_PORT, BAUD_RATE


class SerialService:

    def __init__(self):

        self.connection = None
        self.weight_g = 0.0

    def connect(self):

        try:

            self.connection = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            return True

        except serial.SerialException:

            self.connection = None

            return False

    def loop(self):

        while self.connection and self.connection.is_open:

            try:

                self.connection.write(b'P')

                time.sleep(0.8)

                if self.connection.in_waiting > 0:

                    data = self.connection.read(
                        self.connection.in_waiting
                    )

                    text = data.decode(
                        'utf-8',
                        errors='ignore'
                    ).strip()

                    numbers = re.findall(
                        r'[-+]?\d*\.?\d+',
                        text
                    )

                    if numbers:

                        peso_kg = float(numbers[0])

                        self.weight_g = peso_kg * 1000

                time.sleep(1.5)

            except Exception:

                time.sleep(1)