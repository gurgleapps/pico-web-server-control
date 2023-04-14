"""
    Project: GurgleApps Webserver
    File: main.py
    Author: GurgleApps.com
    Date: 2021-04-01
    Description: Demonstrates how to use the GurgleApps Webserver
"""
import config
from gurgleapps_webserver import GurgleAppsWebserver
import utime as time
import uasyncio as asyncio
from machine import Pin
import ujson as json
from board import Board

BOARD_TYPE = Board().type
print("Board type: " + BOARD_TYPE)

if BOARD_TYPE == Board.BoardType.PICO_W:
    led = Pin("LED", Pin.OUT)
elif BOARD_TYPE == Board.BoardType.PICO:
    led = Pin(25, Pin.OUT)
elif BOARD_TYPE == Board.BoardType.ESP8266:
    led = Pin(2, Pin.OUT)
else:
    led = Pin(2, Pin.OUT)


blink_off_time = 0.5
blink_on_time = 0.5

status = True
shutdown = False

async def example_func(request, response, param1, param2):
    print("example_func")
    print("param1: " + param1)
    print("param2: " + param2)
    response_string = json.dumps({ "param1": param1, "param2": param2, "post_data": request.post_data})
    await response.send_json(response_string, 200)

async def say_hello(request, response, name):
    await response.send_html("Hello " + name + " hope you are well")

async def send_status(request, response):
    # send boolean status and number frequency
    response_string = json.dumps({"status": status, "delay": (blink_off_time + blink_on_time) *0.5, "blink_on_time": blink_on_time, "blink_off_time": blink_off_time})
    await response.send_json(response_string, 200)

async def set_blink_pattern(request, response, on, off):
    print("on: " + on)
    print("off: " + off)
    global blink_off_time, blink_on_time
    blink_off_time = float(off)
    blink_on_time = float(on)
    await send_status(request, response)

async def set_delay(request, response, new_delay):
    print("new delay: " + new_delay)
    global blink_off_time, blink_on_time
    blink_off_time = float(new_delay)
    blink_on_time = float(new_delay) 
    await send_status(request, response)

async def stop_flashing(request, response):
    global status
    status = False
    await send_status(request, response)

async def start_flashing(request, response):
    global status
    status = True
    await send_status(request, response)

async def stop_server(request, response):
    global shutdown
    await response.send_html("Server stopping")
    await server.stop_server()
    shutdown = True


async def background_task():
    global shutdown
    if config.BLINK_IP:
        await(server.blink_ip(led_pin = led, last_only = config.BLINK_LAST_ONLY))
    while not shutdown:
        if status:
            led.on()
            await asyncio.sleep(blink_on_time)
            led.off()
            await asyncio.sleep(blink_off_time)
        else:
            led.off()
            await asyncio.sleep(0.2)

server = GurgleAppsWebserver(config.WIFI_SSID, config.WIFI_PASSWORD, port=80, timeout=20, doc_root="/www", log_level=2)
server.add_function_route("/set-delay/<delay>", set_delay)
server.add_function_route(
    "/set-blink-pattern/<on_time>/<off_time>",
    set_blink_pattern
)
server.add_function_route("/stop", stop_flashing)
server.add_function_route("/start", start_flashing)
server.add_function_route("/status", send_status)
server.add_function_route("/example/func/<param1>/<param2>", example_func)
server.add_function_route("/hello/<name>", say_hello)
server.add_function_route("/stop-server", stop_server)

asyncio.run(server.start_server_with_background_task(background_task))
print('DONE')
