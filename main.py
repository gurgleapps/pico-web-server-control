import config
from gurgleapps_webserver import GurgleAppsWebserver
import utime as time
import uasyncio as asyncio
from machine import Pin
import ujson as json

delay = 0.5
status = True
led = Pin("LED", Pin.OUT)

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
    response_string = json.dumps({"status": status, "delay": delay})
    await response.send_json(response_string, 200)


async def set_delay(request, response, new_delay):
    print("new delay: " + new_delay)
    global delay
    delay = float(new_delay)
    await send_status(request, response)

async def stop_flashing(request, response):
    global status
    status = False
    await send_status(request, response)

async def start_flashing(request, response):
    global status
    status = True
    await send_status(request, response)

async def main():
    await server.start_server()

async def background_task():
    global delay, status
    while True:
        await asyncio.sleep(delay)
        if status:
            led.toggle()
        else:
            led.off()
        

async def run():
    await asyncio.gather(main(), background_task())

server = GurgleAppsWebserver(config.WIFI_SSID, config.WIFI_PASSWORD, port=80, timeout=20, doc_root="/www", log_level=2)
server.add_function_route("/set-delay/<delay>", set_delay)
server.add_function_route("/stop", stop_flashing)
server.add_function_route("/start", start_flashing)
server.add_function_route("/status", send_status)
server.add_function_route("/example/func/<param1>/<param2>", example_func)
server.add_function_route("/hello/<name>", say_hello)

asyncio.run(run())
