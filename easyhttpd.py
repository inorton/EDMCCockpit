import os
import socket
from functools import partial
from http import HTTPStatus
from threading import Thread
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional


# stolen much of this from python3 lib/http/server.py


def _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, _, _, _, sockaddr = next(iter(infos))
    return family, sockaddr


class RequestHandler(SimpleHTTPRequestHandler):
    """
    Handler for static and JSON requests
    """

    def __init__(self, *args, **kwargs):
        super(RequestHandler, self).__init__(*args, **kwargs)

    def translate_path(self, path):
        """
        Convert the (web path) to a local file path relative to the root dir
        :param path:
        :return:
        """
        parts = path.split('/')
        return os.path.join(self.directory, *parts)

    def do_GET(self):
        api = self.server.getapi(self)

        if api:
            try:
                headers, response = api(self)
                self.send_response(HTTPStatus.OK)
                for header in headers:
                    self.send_header(header, headers[header])
                self.end_headers()
                if response:
                    self.wfile.write(response.encode("utf-8"))
                return

            except Exception as err:
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(err))

        super(RequestHandler, self).do_GET()

    def send_head(self):
        """
        Serve local files for GET and HEAD if they exist.
        Redirect missing files to /index.html.
        :return:
        """
        path = self.translate_path(self.path)
        if os.path.exists(path):
            return super(RequestHandler, self).send_head()

        # self.send_error(HTTPStatus.NOT_FOUND, "File not found")
        # return None

        # redirect angular routes to /
        self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        self.send_header("Location", "/index.html")
        self.end_headers()
        return None

    def log_message(self, fmt, *args):
        if "EDTILE_DEBUG" in os.environ:
            super(RequestHandler, self).log_message(fmt, *args)


class Server(ThreadingHTTPServer):
    def __init__(self, server_address, handlerclass, rootdir):
        super().__init__(server_address, handlerclass)
        self.rootdir = os.path.abspath(rootdir)
        self.routes = {}

    def getapi(self, request):
        path = request.path.strip("/")
        return self.routes.get(path, None)


def makeserver(rootdir, protocol="HTTP/1.0", port=3302):
    """
    Run a http server with custom handler
    """
    Server.address_family, addr = _get_best_family("0.0.0.0", port)
    RequestHandler.protocol_version = protocol
    handler = partial(RequestHandler, directory=rootdir)

    httpd = Server(addr, handler, rootdir)
    host, port = httpd.socket.getsockname()[:2]
    url_host = f'[{host}]' if ':' in host else host
    print(
        f"Serving HTTP on {host} port {port} "
        f"(http://{url_host}:{port}/) ..."
    )
    return httpd


class ServerThread(Thread):
    def __init__(self, port: int):
        super(ServerThread, self).__init__(daemon=True)
        self.port = port
        self.rootdir: Optional[str] = None
        self.httpd: Optional[Server] = None

    def setup(self, rootdir: str):
        self.rootdir = rootdir
        self.httpd = makeserver(self.rootdir, port=self.port)

    def run(self):
        self.httpd.serve_forever()

    def add_route(self, path: str, func: callable):
        self.httpd.routes[path] = func



