"""
    Project Name: board.py
    File Name: board.py
    Author: GurgleApps.com
    Date: 2021-04-01
    Description: Detects the board type
"""
import sys
import os

class Board:
    class BoardType:
        PICO_W = 'Raspberry Pi Pico W'
        PICO = 'Raspberry Pi Pico'
        ESP8266 = 'ESP8266'
        ESP32 = 'ESP32'
        UNKNOWN = 'Unknown'

    def __init__(self):
        self.type = self.detect_board_type()

    def detect_board_type(self):
        sysname = os.uname().sysname.lower()
        machine = os.uname().machine.lower()

        if sysname == 'rp2' and 'pico w' in machine:
            return self.BoardType.PICO_W
        elif sysname == 'rp2' and 'pico' in machine:
            return self.BoardType.PICO
        elif sysname == 'esp8266':
            return self.BoardType.ESP8266
        # Add more conditions for other boards here
        else:
            return self.BoardType.UNKNOWN
