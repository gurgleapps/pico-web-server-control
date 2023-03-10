import config
from gurgleapps_webserver import GurgleAppsWebserver
import utime as time

server = GurgleAppsWebserver(config.WIFI_SSID, config.WIFI_PASSWORD)

while True:
        time.sleep(0.1)
    