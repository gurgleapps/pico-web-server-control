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


class GurgleAppsWebserver:

    def __init__(self, wifi_ssid, wifi_password, port=80, timeout=20, doc_root="/www", log_level=0):
        print("GurgleApps.com Webserver")
        self.ip_address = '1.1.1.1'
        self.port = port
        self.timeout = timeout
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.doc_root = doc_root
        self.function_routes = []
        self.log_level = log_level
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

        #if self.wlan.status() != 3:
        if self.wlan.isconnected() == False:
            raise RuntimeError('network connection failed')
        else:
            print('connected')
            status = self.wlan.ifconfig()
            print('ip = ' + status[0])
        self.serving = True
        self.ip_address = status[0]
        print('point your browser to http://', status[0])
        #asyncio.new_event_loop()
        print("exit constructor")

    # async def start_server(self):
    #     print("start_server")
    #     asyncio.create_task(asyncio.start_server(
    #         self.serve_request, "0.0.0.0", 80))
    #     while self.serving:
    #         await asyncio.sleep(0.1)

    async def start_server(self):
        print("start_server")
        server_task = asyncio.create_task(asyncio.start_server(
            self.serve_request, "0.0.0.0", 80))
        await server_task

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
            url = ""
            method = ""
            content_length = 0
            # Read the request line by line because we want the post data potentially
            headers = []
            post_data = None
            while True:
                line = await reader.readline()
                #print("line: "+str(line))
                line = line.decode('utf-8').strip()
                if line == "":
                    break
                headers.append(line)
            request_raw = str("\r\n".join(headers))
            print(request_raw)
            request_pattern = re.compile(r"(GET|POST)\s+([^\s]+)\s+HTTP")
            match = request_pattern.search(request_raw)
            if match:
                method = match.group(1)
                url = match.group(2)
                print(method, url)
            else: # regex didn't match, try splitting the request line
                request_parts = request_raw.split(" ")
                if len(request_parts) > 1:
                    method = request_parts[0]
                    url = request_parts[1]
                    print(method, url)
                else:
                    print("no match")
            # extract content length for POST requests
            if method == "POST":
                content_length_pattern = re.compile(r"Content-Length:\s+(\d+)")
                match = content_length_pattern.search(request_raw)
                if match:
                    content_length = int(match.group(1))
                    print("content_length: "+str(content_length))
            # Read the POST data if there's any
            if content_length > 0:
                post_data_raw = await reader.readexactly(content_length)
                print("POST data:", post_data_raw)
                post_data = json.loads(post_data_raw)
            request = Request(post_data)
            response = Response(writer)
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
            #if uos.stat(file_path)[6] > 0:
            if self.file_exists(file_path):
                content_type = self.get_content_type(url)
                if self.log_level > 1:
                    print("content_type: "+str(content_type))
                await response.send_file(file_path, content_type=content_type)
                return
            if url == "/":
                print("root")
                files_and_folders = self.list_files_and_folders(self.doc_root)
                html = self.generate_root_page_html(files_and_folders)
                await response.send(html)
                return
            print("file not found "+url)
            await response.send(self.html % "page not found "+url, status_code=404)
            if (url == "/shutdown"):
                self.serving = False
        except OSError as e:
            print(e)

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


    def get_content_type(self,file_path):
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
    async def blink_ip(self, led_pin, ip = None, repeat=2, delay_between_digits=0.9, last_only = False):
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
            ip_parts = [ip_parts[-1]] # Only blink the last part of the IP address

        for part in ip_parts:
            for digit in part:
                ip_digits_and_dots.append(int(digit))
            ip_digits_and_dots.append('.')  # Add a dot to the list to represent the separator
        ip_digits_and_dots.pop()  # Remove the last dot
        ip_digits_and_dots.append('-')  # Add a dash to the list to represent the end of the IP address

        for _ in range(repeat):
            for element in ip_digits_and_dots:
                blink_element(element, led_pin)
                await asyncio.sleep(delay_between_digits if element != '.' else 2 * delay_between_digits)
            await asyncio.sleep(delay_between_repititions)

    def list_files_and_folders(self, path):
        files_and_folders = os.listdir(path)
        return files_and_folders

    def generate_root_page_html(self, files_and_folders):
        folder_icon_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="inline-block w-6 h-6">
        <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V8a2 2 0 00-2-2H9.586A2 2 0 018 6H4z" />
        </svg>
        """
        file_icon_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="inline-block w-6 h-6">
        <path d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0016.414 6L13 2.586A2 2 0 0011.414 2H6z" />
        </svg>
        """
        file_list_html = "<ul class='list-none'>"
        for file_or_folder in files_and_folders:
            icon = folder_icon_svg if os.path.isdir(os.path.join("www", file_or_folder)) else file_icon_svg
            file_list_html += f"<li class='my-2'><a href='/{file_or_folder}' class='text-blue-600 hover:text-blue-800'>{icon} {file_or_folder}</a></li>"
        file_list_html += "</ul>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>GurgleApps.com Webserver</title>
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            </head>
            <body class="bg-gray-100">
                <div class="container mx-auto p-8">
                    <h1 class="text-3xl font-bold mb-4">Welcome to GurgleApps.com Webserver</h1>
                    <h2 class="text-2xl mb-2">File List:</h2>
                    {file_list_html}
                </div>
            </body>
        </html>
        """
        return html_content
