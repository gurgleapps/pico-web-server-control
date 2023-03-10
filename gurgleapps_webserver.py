import network
import socket
import time
import re
import config
import uos


class GurgleAppsWebserver:

    def __init__(self, wifi_ssid, wifi_password, port=80, timeout=20, doc_root="/www"):
        print("GurgleApps.com Webserver")
        self.port = port
        self.timeout = timeout
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.doc_root = doc_root
        # wifi client in station mode so we can connect to an access point
        self.wlan = network.WLAN(network.STA_IF)
        # activate the interface
        self.wlan.active(True)
        # connect to the access point with the ssid and password
        self.wlan.connect(self.wifi_ssid, self.wifi_password)

        self.html = """<!DOCTYPE html>
        <html>
            <head> <title>GurgleApps.com Webserver</title> </head>
            <body> <h1>Pico W</h1>
                <p>%s</p>
            </body>
        </html>
        """
        counter = self.timeout
        while counter > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            counter -= 1
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
        print('point your browser to http://', status[0])

        while self.serving:
            self.listen_for_request()
            

    def listen_for_request(self):
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
            file = self.get_file(self.doc_root + url)
            print("file: "+str(file))
            if file:
                print("file found so serving it")
                print(file)
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                cl.send(file)
                cl.close()
                return
            print("file not found")
            response = self.html % "page not found "+url
            cl.send('HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
            if (url == "/shutdown"):
                self.socket.close()
                self.serving = False
                print('connection closed')
            cl.close()
        except OSError as e:
            cl.close()
            print('connection closed')

    def get_file(self, filename):
        print("getFile: "+filename)
        try :
            # Check if the file exists
            if uos.stat(filename)[6] > 0:
                # Open the file in read mode
                with open(filename, "r") as f:
                    # Read the contents of the file into a string
                    return f.read()
            else:
                # The file doesn't exist
                return False
        except OSError as e:
            # print the error
            print(e)
            return False
