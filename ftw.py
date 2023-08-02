import http.server

class ftws(http.server.BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Frank's Terrible WebUI</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>Yo.</body></html>", "utf-8"))

http.server.HTTPServer(('', 8000), ftws).serve_forever()
