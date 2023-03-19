import config
from gurgleapps_webserver import GurgleAppsWebserver
import utime as time
import uasyncio as asyncio

async def send_status(writer):
    writer.write('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
    # send boolean status and number frequency
    response = "{status: " + str(status) + ", freq: " + str(frequency) + "}"
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()

async def set_frequency(writer, freq):
    global frequency
    frequency = freq
    await send_status(writer)

async def stop_generating(writer):
    global status
    status = False
    await send_status(writer)

async def start_generating(writer):
    global status
    status = True
    await send_status(writer)

async def main():
    await server.start_server()

async def background_task():
    while True:
        await asyncio.sleep(10)
        print("main")

async def run():
    await asyncio.gather(main(), background_task())

server = GurgleAppsWebserver(config.WIFI_SSID, config.WIFI_PASSWORD)
server.add_function_route("^/set-frequency/(\d+)$", set_frequency)
server.add_function_route("^/stop$", stop_generating)
server.add_function_route("^/start$", start_generating)

frequency = 20
status = True

asyncio.run(run())
