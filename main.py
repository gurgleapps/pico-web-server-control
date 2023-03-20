import config
from gurgleapps_webserver import GurgleAppsWebserver
import utime as time
import uasyncio as asyncio
from machine import Pin
import ujson as json

delay = 0.5
status = True
led = Pin("LED", Pin.OUT)

async def send_status(writer):
    writer.write('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
    # send boolean status and number frequency
    response = json.dumps({"status": status, "delay": delay})
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()

async def set_delay(writer, new_delay):
    print("new delay: " + new_delay)
    global delay
    delay = float(new_delay)
    await send_status(writer)

async def stop_flashing(writer):
    global status
    status = False
    await send_status(writer)

async def start_flashing(writer):
    global status
    status = True
    await send_status(writer)

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

server = GurgleAppsWebserver(config.WIFI_SSID, config.WIFI_PASSWORD)
server.add_function_route("^/set-delay/(\d+(?:\.\d+)?)$", set_delay)
server.add_function_route("^/stop$", stop_flashing)
server.add_function_route("^/start$", start_flashing)
server.add_function_route("^/status$", send_status)

asyncio.run(run())
