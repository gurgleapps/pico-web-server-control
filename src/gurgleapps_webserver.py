"""
    Project: GurgleApps Web Server
    File: gurgleapps_webserver.py
    Author: GurgleApps.com
    Date: Your Date 2023-04-01
    Description: GurgleApps Web Server
"""
import network
import re
import time
import uos
import uasyncio as asyncio
import ujson as json
from response import Response
from request import Request
import gc
import os
import machine


class GurgleAppsWebserver:

    def __init__(self, wifi_ssid, wifi_password, port=80, timeout=20, doc_root="/www", log_level=0):
        print("GurgleApps.com Webserver")
        self.default_index_pages = [] # ["index.html", "index.htm"]
        self.ip_address = '1.1.1.1'
        self.port = port
        self.timeout = timeout
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.ap_ssid = None
        self.ap_password = None
        self.doc_root = doc_root
        self.function_routes = []
        self.log_level = log_level
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.enable_cors = False
        self.html = """<!DOCTYPE html>
        <html>
            <head> <title>GurgleApps.com Webserver</title> </head>
            <body> <h1>Pico W</h1>
                <p>%s</p>
            </body>
        </html>
        """
        if self.wifi_ssid!=None:
            if self.connect_wifi(self.wifi_ssid, self.wifi_password):
                print('point your browser to http://', self.ip_address)
            else:
                raise RuntimeError('network connection failed')
        self.server_running = False
        

    async def connect_wifi(self, ssid, password):
        try:
            self.wifi_ssid = ssid
            self.wifi_password = password
            # Deactivate AP mode
            #self.wlan_ap.active(False)
            if self.wlan_sta.isconnected():
                print("Already connected to Wi-Fi. IP: "+self.wlan_sta.ifconfig()[0])
                self.wlan_sta.disconnect()
                self.wlan_sta.active(False)
                #time.sleep(1)
                await asyncio.sleep(1)
                print("Disconnected from Wi-Fi.")
            else:
                print("Not connected to Wi-Fi.")

            # Activate Wi-Fi mode and connect
            self.wlan_sta.active(True)
            #time.sleep(1)
            await asyncio.sleep(1)
            self.wlan_sta.connect(ssid, password)
            # Wait for connection
            print("Connecting to Wi-Fi...")
            for _ in range(self.timeout):
                #time.sleep(1)
                await asyncio.sleep(1)
                if self.wlan_sta.isconnected():
                    self.ip_address = self.wlan_sta.ifconfig()[0]
                    print(f"Connected to Wi-Fi. IP: {self.ip_address}")
                    return True
            print("Failed to connect to Wi-Fi.")
            return False
        except OSError as e:
            print(f"Error connecting to Wi-Fi: {e}")
            return False
        
    def is_wifi_connected(self):
        return self.wlan_sta.isconnected()
    
    def is_access_point_active(self):
        return self.wlan_ap.active()
    
    def get_wifi_ssid(self):
        return self.wifi_ssid
    
    def get_wifi_ip_address(self):
        return self.wlan_sta.ifconfig()[0]
    
    def get_ap_ssid(self):
        return self.wlan_ap.config('essid')
        return self.ap_ssid
    
    def get_ap_ip_address(self):
        return self.wlan_ap.ifconfig()[0]
    
    def get_ip_address(self):
        return self.ip_address
    
    def start_access_point(self, ssid, password=None):
    #def connect_access_point(self, ssid, password=None, ip='192.168.1.1', subnet='255.255.255.0', gateway='192.168.1.1', dns='8.8.8.8'):
        # Set the IP configuration for the AP mode
        #self.wlan_ap.ifconfig((ip, subnet, gateway, dns))
        self.ap_ssid = ssid
        self.ap_password = password
        if os.uname().sysname == 'esp32':
            self.wlan_ap.active(True) # ESP32 needed this before config
        self.wlan_ap.config(essid=ssid, password=password)
        if os.uname().sysname != 'esp32':
            self.wlan_ap.active(True)
        print(f"AP Mode started. SSID: {self.get_ap_ssid()}, IP: {self.get_ap_ip_address()}")
        # pico needs a cycle or ssid is PICO-xxxx
        if self.get_ap_ssid() != ssid:
            print("AP SSID incorrect: "+self.get_ap_ssid())
            machine.reset()
        return True
    
    async def maintain_connection(self):
        while True:
            if self.wlan_sta.isconnected() == False and self.wifi_ssid != None:
                print("Lost connection to Wi-Fi. Attempting to reconnect...")
                self.connect_wifi(self.wifi_ssid, self.wifi_password)
            await asyncio.sleep(20)


    async def start_server(self):
        print("start_server")
        self.server = await asyncio.start_server(
            self.serve_request, "0.0.0.0", self.port
        )

    async def stop_server(self):
        if self.server is not None:
            self.server.close()
        await self.server.wait_closed()
        self.server = None
        print("stop_server")

    async def start_server_with_background_task(self, background_task):
        async def main():
            await asyncio.gather(
                self.start_server(), 
                background_task(),
                self.maintain_connection()
                )
        await main()

    def set_default_index_pages(self, default_index_pages):
        self.default_index_pages = default_index_pages

    def set_cors(self, enable_cors=True):
        self.enable_cors = enable_cors

    # async def start_server(self):
    #     print("start_server")
    #     server = await asyncio.start_server(
    #         self.serve_request, "0.0.0.0", 80)
    #     async with server:
    #         await server.serve_forever()

    def add_function_route(self, route, function):
        self.function_routes.append({"route": route, "function": function})

    async def serve_request(self, reader, writer):
        gc.collect()
        try:
            response = Response(writer, enable_cors=self.enable_cors)
            url = ""
            method = ""
            content_length = 0
            # Read the request line by line because we want the post data potentially
            headers = []
            post_data = None
            while True:
                line = await reader.readline()
                # print("line: "+str(line))
                line = line.decode('utf-8').strip()
                if line == "":
                    break
                headers.append(line)
            request_raw = str("\r\n".join(headers))
            if self.log_level > 0:
                print(request_raw)
            request_pattern = re.compile(r"(GET|POST|OPTIONS)\s+([^\s]+)\s+HTTP")
            match = request_pattern.search(request_raw)
            if match:
                method = match.group(1)
                url = match.group(2)
                if self.log_level > 0:
                    print(method, url)
            else:  # regex didn't match, try splitting the request line
                request_parts = request_raw.split(" ")
                if len(request_parts) > 1:
                    method = request_parts[0]
                    url = request_parts[1]
                    if self.log_level > 0:
                        print(method, url)
                elif self.log_level > 0:
                    print("no match")
            if method == "OPTIONS":
                # Handle preflight requests
                await response.send("", status_code=204)
                return
            # extract content length for POST requests
            if method == "POST":
                content_length_pattern = re.compile(r"Content-Length:\s+(\d+)")
                match = content_length_pattern.search(request_raw)
                if match:
                    content_length = int(match.group(1))
                    if self.log_level > 0:
                        print("content_length: "+str(content_length))
            # Read the POST data if there's any
            if content_length > 0:
                post_data_raw = await reader.readexactly(content_length)
                if self.log_level > 0:
                    print("POST data:", post_data_raw)
                content_type_header = "Content-Type: application/json"  # default to JSON
                for header in headers:
                    if header.lower().startswith("content-type:"):
                        content_type_header = header
                        break
                if "application/json" in content_type_header.lower():
                    try:
                        if self.log_level > 0:
                            print("decoding JSON data")
                        post_data = json.loads(post_data_raw)
                    except ValueError as e:
                        print("Error decoding JSON data:", e)
                        # Handle the error (e.g., send an error response to the client)
                        await response.send("Invalid JSON data", status_code=400)
                        return
                elif "application/x-www-form-urlencoded" in content_type_header.lower():
                    post_data = self.parse_form_data(post_data_raw.decode('utf-8'))
                else:
                    # Handle unsupported content types
                    await response.send("Unsupported content type", status_code=415)
                    return
            request = Request(post_data)
            # check if the url is a function route and if so run the function
            path_components = self.get_path_components(url)
            print("path_components: "+str(path_components))
            route_function, params = self.match_route(path_components)
            if route_function:
                print("calling function: "+str(route_function) +
                      " with params: "+str(params))
                await route_function(request, response, *params)
                return
            # perhaps it is a file
            file_path = self.doc_root + url
            if self.log_level > 0:
                print("file_path: "+str(file_path))
            # if uos.stat(file_path)[6] > 0:
            if self.file_exists(file_path): #serve a file
                content_type = self.get_content_type(url)
                if self.log_level > 1:
                    print("content_type: "+str(content_type))
                await response.send_file(file_path, content_type=content_type)
                return
            # perhaps it is a folder
            if self.dir_exists(file_path): #serve a folder
                for index_page in self.default_index_pages:
                    index_file_path = file_path.rstrip("/") + "/" + index_page
                    if self.log_level > 1:
                        print("index_file_path: "+str(index_file_path))
                    if self.file_exists(index_file_path):
                        print("serving index file: "+index_file_path)
                        await response.send_file(index_file_path, content_type=self.get_content_type(index_file_path))
                        return
                files_and_folders = self.list_files_and_folders(file_path)
                await response.send_iterator(self.generate_root_page_html(files_and_folders))
                return
            # if url == "/":
            #     print("root")
            #     files_and_folders = self.list_files_and_folders(self.doc_root)
            #     await response.send_iterator(self.generate_root_page_html(files_and_folders))
            #     return
            print("file not found "+url)
            await response.send(self.html % "page not found "+url, status_code=404)
            if (url == "/shutdown"):
                self.serving = False
        except OSError as e:
            print(e)
            
    def parse_form_data(self, form_data_raw):
        form_data = {}
        for pair in form_data_raw.split('&'):
            key, value = pair.split('=')
            form_data[self.url_decode(key)] = self.url_decode(value)
        return form_data
    
    def url_decode(self, encoded_str):
        decoded_str = ""
        i = 0
        while i < len(encoded_str):
            if encoded_str[i] == '%':
                hex_code = encoded_str[i + 1:i + 3]
                char = chr(int(hex_code, 16))
                decoded_str += char
                i += 3
            else:
                decoded_str += encoded_str[i]
                i += 1
        return decoded_str


    def dir_exists(self, filename):
        try:
            return (os.stat(filename)[0] & 0x4000) != 0
        except OSError:
            return False

    def file_exists(self, filename):
        try:
            return (os.stat(filename)[0] & 0x4000) == 0
        except OSError:
            return False

    def get_file(self, filename):
        print("getFile: "+filename)
        try:
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

    def get_path_components(self, path):
        print("get_path_components: "+path)
        return tuple(filter(None, path.split('/')))

    def match_route(self, path_components):
        for route in self.function_routes:
            route_pattern = list(filter(None, route["route"].split("/")))
            if self.log_level > 1:
                print("route_pattern: "+str(route_pattern))
            if len(route_pattern) != len(path_components):
                continue
            match = True
            params = []
            for idx, pattern_component in enumerate(route_pattern):
                if self.log_level > 2:
                    print("pattern_component: "+str(pattern_component))
                if pattern_component.startswith('<') and pattern_component.endswith('>'):
                    param_value = path_components[idx]
                    params.append(param_value)
                else:
                    if pattern_component != path_components[idx]:
                        match = False
                        break
            if match:
                return route["function"], params
        return None, []

    def get_file_extension(self, file_path):
        file_parts = file_path.split('.')
        if len(file_parts) > 1:
            return file_parts[-1]
        return ''

    def get_content_type(self, file_path):
        extension = self.get_file_extension(file_path)
        content_type_map = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'ico': 'image/x-icon',
            'svg': 'image/svg+xml',
            'json': 'application/json',
            'xml': 'application/xml',
            'pdf': 'application/pdf',
            'zip': 'application/zip',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'mp3': 'audio/mpeg',
            'mp4': 'video/mp4',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'webm': 'video/webm',
        }
        return content_type_map.get(extension, 'text/plain')

    # long pause for dots 4 quick blinks for zero 2 quick for a dot
    async def blink_ip(self, led_pin, ip=None, repeat=2, delay_between_digits=0.9, last_only=False):
        delay_between_repititions = 2
        if ip == None:
            ip = self.ip_address
        print("blink_ip: " + str(ip))

        def blink_element(element, pin, duration=0.27):
            if element == '-':
                blinks = 9
                duration = 0.1
            elif element == '.':
                blinks = 2
                duration = 0.1
            elif element == 0:
                blinks = 4
                duration = 0.1
            else:
                blinks = element

            for _ in range(blinks):
                pin.on()
                time.sleep(duration)
                pin.off()
                time.sleep(duration)

        ip_digits_and_dots = []
        ip_parts = ip.split('.')
        if last_only:
            # Only blink the last part of the IP address
            ip_parts = [ip_parts[-1]]

        for part in ip_parts:
            for digit in part:
                ip_digits_and_dots.append(int(digit))
            # Add a dot to the list to represent the separator
            ip_digits_and_dots.append('.')
        ip_digits_and_dots.pop()  # Remove the last dot
        # Add a dash to the list to represent the end of the IP address
        ip_digits_and_dots.append('-')

        for _ in range(repeat):
            for element in ip_digits_and_dots:
                blink_element(element, led_pin)
                await asyncio.sleep(delay_between_digits if element != '.' else 2 * delay_between_digits)
            await asyncio.sleep(delay_between_repititions)


    def list_files_and_folders(self, path):
        entries = uos.ilistdir(path)
        path = path.replace(self.doc_root, '')
        # remove all leading slashes
        path = path.lstrip('/')
        files_and_folders = []
        # print("list_files_and_folders: "+path)
        # print("list_files_and_folders: "+self.doc_root)
        if path != self.doc_root and path != self.doc_root + '/':
            files_and_folders.append({"name": "..", "type": "directory", "path": path+"/.."})
        for entry in entries:
            name = entry[0]
            mode = entry[1]
            if mode & 0o170000 == 0o040000:  # Check if it's a directory
                files_and_folders.append({"name": name, "type": "directory", "path": path+"/"+name})
            elif mode & 0o170000 == 0o100000:  # Check if it's a file
                files_and_folders.append({"name": name, "type": "file", "path": path+"/"+name})
        return files_and_folders

    def generate_root_page_html(self, files_and_folders):
        yield """
       <!DOCTYPE html>
        <html>
            <head>
                <title>GurgleApps.com Webserver</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="/styles.css" rel="stylesheet">
            </head>
            <body class="bg-gray-100">
        """
        yield """
        <div class="relative flex min-h-screen flex-col justify-center overflow-hidden bg-gray-50 py-6 sm:py-12">
        <div class="relative bg-white px-6 pb-8 pt-10 shadow-xl ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg sm:rounded-lg sm:px-10">
        <div class="mx-auto max-w-md">
        <a href="https://gurgleapps.com"><img src="/img/logo.svg" class="h-12 w-auto" alt="GurgleApps.com"></a>
        """
        yield """
        <div class="divide-y divide-gray-300/50">
        <div class="space-y-6 py-8 text-base leading-7 text-gray-600">
          <h1 class="text-lg font-semibold">Welcome to GurgleApps.com Webserver</h1>
          <h12 class="text-base font-semibold">File List:</h2>
          <ul class="mt-3">
        """
        folder_icon_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
        <path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-15a3 3 0 00-3 3V18a3 3 0 003 3h15zM1.5 10.146V6a3 3 0 013-3h5.379a2.25 2.25 0 011.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 013 3v1.146A4.483 4.483 0 0019.5 9h-15a4.483 4.483 0 00-3 1.146z" />
        </svg>
        """
        file_icon_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
        <path d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0016.5 9h-1.875a1.875 1.875 0 01-1.875-1.875V5.25A3.75 3.75 0 009 1.5H5.625z" />
        <path d="M12.971 1.816A5.23 5.23 0 0114.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 013.434 1.279 9.768 9.768 0 00-6.963-6.963z" />
        </svg>
        """
        for index, file_or_folder in enumerate(files_and_folders):
                icon = folder_icon_svg if file_or_folder['type'] == 'directory' else file_icon_svg
                text_class = 'text-blue-500' if file_or_folder['type'] == 'directory' else 'text-blue-600' 
                bg_class = "" if index % 2 == 1 else "bg-gray-50"
                yield f"<li class='border-t border-gray-300 py-1.5 {bg_class}'><a href='{file_or_folder['path']}' class='flex items-center font-semibold {text_class} hover:text-blue-700'>{icon}<p class='ml-2'>{file_or_folder['name']}</p></a></li>"
        yield "</ul>"
        # Closing tags for the body and container div
        yield """
        </div>
        <div class="pt-3 text-base font-semibold leading-7">
        <p class="text-gray-900">More information</p><p><a href="https://gurgleapps.com/learn/projects/micropython-web-server-control-raspberry-pi-pico-projects" class="text-indigo-500 hover:text-sky-600">Project Home &rarr;</a>
        </p></div></div></div></div></div></body></html>
        """
       

