# response.py

class Response:
    def __init__(self, writer):
        self.writer = writer

    async def send(self, status, content_type, content):
        self.writer.write(f'HTTP/1.0 {status}\r\nContent-type: {content_type}\r\n\r\n')
        self.writer.write(content)
        await self.writer.drain()
        await self.writer.wait_closed()