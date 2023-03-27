# response.py

class Response:
    def __init__(self, writer):
        self.writer = writer

    async def send(self, body, status_code = 200, content_type = "text/html"):
        self.writer.write(f'HTTP/1.0 {status_code}\r\nContent-type: {content_type}\r\n\r\n')
        self.writer.write(body)
        await self.writer.drain()
        await self.writer.wait_closed()

    async def send_html(self, body, status_code=200):
        await self.send(body, status_code, content_type='text/html')

    async def send_json(self, body, status_code=200):
        await self.send(body, status_code, content_type='application/json')