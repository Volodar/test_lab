from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler


class HttpServer(BaseHTTPRequestHandler):
    request_handler_class = None

    @staticmethod
    def start(url, port, request_handler_class):
        HttpServer.request_handler_class = request_handler_class
        server = HTTPServer((url, port), HttpServer)
        return server

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            s = self.path

            payload = s
            address = self.client_address
            request_handler = HttpServer.request_handler_class(self)
            request_handler.handle(address, payload)

        except Exception as inst:
            self.wfile.write("error({})".format(inst))
            print("error({})".format(inst))

    def send(self, message):
        self.wfile.write(message)