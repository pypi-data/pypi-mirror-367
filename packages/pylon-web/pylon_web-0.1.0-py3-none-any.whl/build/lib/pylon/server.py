import asyncio
from httptools import HttpRequestParser
from markdown import markdown
from typing import Callable, Any
from urllib.parse import unquote
import re

class PylonServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        self.host, self.port = host, port
        self.router = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def route(self, path: str, method: str = 'GET'):
        def decorator(handler: Callable):
            normalized_path = unquote(path).lower()
            self.router[(normalized_path, method.upper())] = handler
            return handler
        return decorator

    def _is_markdown(self, text: str) -> bool:
        """Определяет, содержит ли текст Markdown-разметку"""
        patterns = [
            r'^\s*#',         # Заголовки
            r'\*\*.*\*\*',    # Жирный текст
            r'\*.*\*',        # Курсив
            r'\[.*\]\(.*\)',  # Ссылки
            r'^\s*[-*+] '     # Списки
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    async def _handle_request(self, reader, writer):
        try:
            data = await reader.read(4096)
            req = {'path': '', 'method': 'GET', 'headers': {}}
            
            class Parser:
                def on_url(self, url: bytes): 
                    req['path'] = unquote(url.decode('utf-8')).lower()
                def on_header(self, name: bytes, value: bytes): 
                    req['headers'][name.decode('utf-8').lower()] = value.decode('utf-8')
            
            parser = HttpRequestParser(Parser())
            parser.feed_data(data)
            req['method'] = parser.get_method().decode('utf-8').upper() if parser.get_method() else 'GET'
            
            if handler := self.router.get((req['path'], req['method'])):
                import inspect
                params = inspect.signature(handler).parameters
                response = handler(req) if params else handler()
                
                if isinstance(response, str):
                    if self._is_markdown(response):
                        # Автоматическое преобразование ссылок типа example.com
                        response = re.sub(
                            r'(https?://[^\s]+)|([^\s]+\.[^\s]{2,})',
                            lambda m: f"[{m.group(0)}]({m.group(1) or 'http://' + m.group(0)})",
                            response
                        )
                        response = markdown(response)
                    response = response.encode('utf-8')
                
                writer.write(
                    b"HTTP/1.1 200 OK\r\n" +
                    b"Content-Type: text/html; charset=utf-8\r\n" +
                    f"Content-Length: {len(response)}\r\n\r\n".encode('utf-8') + 
                    response
                )
            else:
                writer.write(
                    b"HTTP/1.1 404 Not Found\r\n"
                    b"Content-Type: text/plain; charset=utf-8\r\n"
                    b"Content-Length: 9\r\n\r\n"
                    b"Not Found"
                )
        
        except Exception as e:
            error = f"500 Server Error: {str(e)}".encode('utf-8')
            writer.write(
                b"HTTP/1.1 500 Internal Server Error\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n" +
                f"Content-Length: {len(error)}\r\n\r\n".encode('utf-8') + 
                error
            )
        finally:
            await writer.drain()
            writer.close()

    def run(self):
        try:
            server = asyncio.start_server(
                self._handle_request,
                self.host,
                self.port,
                reuse_address=True,
                backlog=100
            )
            self.loop.run_until_complete(server)
            print(f"🚀 Pylon запущен на http://{self.host}:{self.port}")
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        finally:
            self.loop.close()