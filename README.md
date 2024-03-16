# Raspberry Pi Pico Web Server Control

This repository contains code to control Raspberry Pi Pico, ESP8266, ESP32 or other MicroPython projects using a browser-based user interface. It allows you to interact with your Pico projects remotely from any device with a web browser, including smartphones, tablets, and computers.

The latest features include improved memory usage, support for additional microcontrollers like ESP8266, and convenient options such as blinking the IP address using the built-in LED and displaying a file list for the root directory.

[![MicroPython Web Server Control](https://gurgleapps.com/assets/image-c/57/57b4760a0b877276a836a75bd107f158576c23b4.webp)](https://gurgleapps.com/learn/projects/micropython-web-server-control-raspberry-pi-pico-projects)

## Features

- Serve static and dynamic web pages from your Raspberry Pi Pico
- Run Python functions on your microcontroller device from a web browser
- Create dynamic web pages with live data from your Pico or other Microcontroller
- Run as ACcess Point (AP) or connect to your Wi-Fi network
- Blink the IP address using the built-in LED, handy when you're out in the field with no screen or computer
- Display a file and folder list of your root directory with an attractive and responsive user interface
- End-to-end examples showcasing various functionalities
- Easily customizable codebase
- Support for ESP8266 and ESP32 microcontrollers


## Setup

1. Make sure you have MicroPython on your Pico
2. Clone this repository
3. Copy the code from the /src folder to your Pico
4. Edit `config.py` with your Wi-Fi details and IP blink options:
   - `WIFI_SSID`: Set this to your Wi-Fi network SSID (e.g., `"your_wifi_ssid"`)
   - `WIFI_PASSWORD`: Set this to your Wi-Fi network password (e.g., `"your_wifi_password"`)
   - `BLINK_IP`: Set this to `True` if you want the Pico to blink its IP address using the built-in LED; set it to `False` if not
   - `BLINK_LAST_ONLY`: Set this to `True` if you want to blink only the last octet of the IP address; set it to `False` to blink the entire IP address
5. Run `main.py` and look for the IP address of your web server
6. Point your browsers to http://<YOUR_IP>

## Using .py or .mpy files

This repository provides both `.py` and `.mpy` files for most modules. While the `.py` files are standard Python files, the `.mpy` files are precompiled MicroPython bytecode files. Using `.mpy` files can result in reduced memory usage and faster execution times on your microcontroller.

### Recommendations
- For most microcontrollers, you can choose between `.py` and `.mpy` files based on your preference.
- For ESP8266, due to its limited memory, it is recommended to use `.mpy` files for modules other than `main.py` and `config.py`.

To choose between `.py` and `.mpy` files, follow these steps:

1. Copy `main.py` and `config.py` from the root directory to your microcontroller.
2. Choose between the `.py` and `.mpy` files for the remaining modules:
   - If you prefer to use the standard Python files, copy the corresponding files from the root directory to your microcontroller.
   - If you prefer to use the precompiled MicroPython bytecode files, copy the corresponding files from the `mpy` folder to your microcontroller.

Remember to customize `config.py` with your Wi-Fi details and other settings before running the code.


## Documentation

For detailed instructions and a step-by-step guide on how to use this project, please refer to our article:

[MicroPython Web Server: Control Your Raspberry Pi Pico Projects Remotely](https://gurgleapps.com/learn/projects/micropython-web-server-control-raspberry-pi-pico-projects)

## Contribute

We'd love to see your projects, control panels, and improvements. Be sure to use this Github repo and submit your additions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
