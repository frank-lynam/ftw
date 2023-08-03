import os, http.server, json

def ftw(f):
  def w(*args, **kwargs):
    return f(*args, **kwargs)
  return w

if __name__=="__main__":
  # Find modules and determine what to do with them
  files = [f for f in os.listdir() 
           if f.lower().endswith("py") and f != "ftw.py"]

  # Logic:
  #  @noftw - ignore file
  #  no @ftw - everything goes online
  #  has @ftw - only decorated functions
  def methods(f):
    with open(f) as fl:
      t = fl.read()
    if "@noftw" in t.lower():
      return None
    if "@ftw" in t.lower():
        return {x.split("def ")[1].split("(")[0].strip():[] for x in t.split("@ftw")[1:]}
    return {x.split("(")[0].strip():[] for x in t.split("def ")[1:]}

  apps = {f[:-3]:methods(f) for f in files}
  apps = {k:v for k,v in apps.items() if v!=None}

  for app in apps.keys():
    __import__(app)
    for meth in apps[app].keys():
      if len(meth)==0:
        apps[app][meth] = [] 

  class ftws(http.server.BaseHTTPRequestHandler):
    def ww(s, txt):
      s.wfile.write(bytes(txt, "utf-8"))

    def do_GET(s):
      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()
      s.ww("<html><head><title>Frank's Terrible WebUI</title></head>")
      s.ww(f"<body><p>Yo.</p><p>The files are:<br/>{files}</p>")
      s.ww(f"<p>The apps are:<br/>{json.dumps(apps, indent=2)}</p></body></html>")

  print(f"Frank's Terrible WebUI found {len(apps.keys())} apps.\nPress Ctrl+C to exit.")
  http.server.HTTPServer(('', 8000), ftws).serve_forever()
