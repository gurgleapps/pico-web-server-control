# Raspberry Pi Pico Web Server Control

This repository contains code to control Raspberry Pi Pico, ESP8266, ESP32 or other MicroPython projects using a browser-based user interface. It allows you to interact with your Pico projects remotely from any device with a web browser, including smartphones, tablets, and computers.

The latest features include improved memory usage, support for additional microcontrollers like ESP8266, and convenient options such as blinking the IP address using the built-in LED and displaying a file list for the root directory.

[![MicroPython Web Server Control](https://gurgleapps.com/assets/image-c/57/57b4760a0b877276a836a75bd107f158576c23b4.webp)](https://gurgleapps.com/learn/projects/micropython-web-server-control-raspberry-pi-pico-projects)

## Features

- Serve static and dynamic web pages from your Raspberry Pi Pico
- Run Python functions on your microcontroller device from a web browser
- Create dynamic web pages with live data from your Pico or other Microcontroller
- Blink the IP address using the built-in LED, handy when you're out in the field with no screen or computer
- Display a file and folder list of your root directory with an attractive and responsive user interface
- End-to-end examples showcasing various functionalities
- Easily customizable codebase

## Setup

1. Make sure you have MicroPython on your Pico
2. Clone this repository
3. Copy the code to your Pico
4. Edit `config.py` with your Wi-Fi details and IP blink options:
   - `WIFI_SSID`: Set this to your Wi-Fi network SSID (e.g., `"your_wifi_ssid"`)
   - `WIFI_PASSWORD`: Set this to your Wi-Fi network password (e.g., `"your_wifi_password"`)
   - `BLINK_IP`: Set this to `True` if you want the Pico to blink its IP address using the built-in LED; set it to `False` if not
   - `BLINK_LAST_ONLY`: Set this to `True` if you want to blink only the last octet of the IP address; set it to `False` to blink the entire IP address
5. Run `main.py` and look for the IP address of your web server
6. Point your browsers to http://<YOUR_IP>


## Documentation

For detailed instructions and a step-by-step guide on how to use this project, please refer to our article:

[MicroPython Web Server: Control Your Raspberry Pi Pico Projects Remotely](https://gurgleapps.com/learn/projects/micropython-web-server-control-raspberry-pi-pico-projects)

## Contribute

We'd love to see your projects, control panels, and improvements. Be sure to use this Github repo and submit your additions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
