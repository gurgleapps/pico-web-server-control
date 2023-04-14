import os

class Response:
    def __init__(self, writer):
        self.writer = writer

    async def send_headers(self, status_code=200, content_type="text/html", content_length=None):
        headers = f'HTTP/1.0 {status_code}\r\nContent-type: {content_type}\r\n'
        if content_length is not None:
            headers += f'Content-Length: {content_length}\r\n'
        headers += '\r\n'
        self.writer.write(headers)
        await self.writer.drain()

    async def send(self, body, status_code=200, content_type="text/html"):
        await self.send_headers(status_code, content_type)
        self.writer.write(body)
        await self.writer.drain()
        await self.writer.wait_closed()

    async def send_html(self, body, status_code=200):
        await self.send(body, status_code, content_type='text/html')

    async def send_json(self, body, status_code=200):
        await self.send(body, status_code, content_type='application/json')

    async def send_file(self, file_path, status_code=200, content_type="text/html"):
        try:
            file_size = os.stat(file_path)[6]
            await self.send_headers(status_code, content_type, content_length=file_size)

            #chunk_size = 1024  # Adjust the chunk size as needed
            #chunk_size = 512  # Adjust the chunk size as needed
            chunk_size = 256
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    self.writer.write(chunk)
                    await self.writer.drain()

            await self.writer.wait_closed()

        except Exception as e:
            print("Error sending file:", e)
            await self.send('', status_code=404)

    async def send_iterator(self, iterator, status_code=200, content_type="text/html"):
        await self.send_headers(status_code=status_code, content_type=content_type)
        for chunk in iterator:
            self.writer.write(chunk)
            await self.writer.drain()
        await self.writer.wait_closed()

