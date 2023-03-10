import network
import socket
import time
import re
import config

class GurgleAppsWebserver:
    def __init__(self, wifi_ssid, wifi_password, port=80, max_wait=20):
        print("GurgleApps.com Webserver")
        self.port = port
        self.max_wait = max_wait
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        self.html = """<!DOCTYPE html>
        <html>
            <head> <title>GurgleApps.com Webserver</title> </head>
            <body> <h1>Pico W</h1>
                <p>%s</p>
            </body>
        </html>
        """
        
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)

        if self.wlan.status() != 3:
            raise RuntimeError('network connection failed')
        else:
            print('connected')
            status = self.wlan.ifconfig()
            print('ip = ' + status[0])

        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]

        self.socket = socket.socket()
        self.socket.bind(addr)
        self.socket.listen(1)
        self.serving = True
        print('point your browser to http://', addr)
        
        while self.serving:
            try:
                url = ""
                cl, addr = self.socket.accept()
                print('client connected from', addr)
                request = cl.recv(1024)
                print(request)
                request = str(request)
                url_pattern = re.compile(r"GET\s+([^\s]+)\s+HTTP")
                match = url_pattern.search(request)
                if match:
                    url = match.group(1)
                    print(url)
                    
                response = self.html % "the url is "+url

                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                cl.send(response)
                cl.close()
                if (url=="/shutdown"):
                    self.socket.close()
                    self.serving = False
                    print('connection closed')

            except OSError as e:
                cl.close()
                print('connection closed')