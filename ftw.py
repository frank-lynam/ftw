import sys, os, http.server, json

def ftw(f):
  def w(*args, **kwargs):
    return f(*args, **kwargs)
  return w

if __name__=="__main__":
  if len(sys.argv) > 1:
    p = sys.argv[1]
    p += "" if p.endswith("/") else "/"
    sys.path.append(p)

  # Find modules and determine what to do with them
  files = [f for f in os.listdir(p) 
           if f.lower().endswith("py") and f != "ftw.py"]

  # Logic:
  #  @noftw - ignore file
  #  no @ftw - everything goes online
  #  has @ftw - only decorated functions
  def methods(f):
    with open(f"{p}{f}") as fl:
      t = fl.read()
    if "@noftw" in t.lower():
      return None
    if "@ftw" in t.lower():
      return {x.split("def ")[1].split("(")[0].strip():[] for x in t.split("@ftw")[1:]}
    return {x.split("(")[0].strip():[] for x in t.split("def ")[1:]}

  apps = {f[:-3]:methods(f) for f in files}
  apps = {k:v for k,v in apps.items() if v!=None}

  for app in apps.keys():
    mod=__import__(app)
    for meth in apps[app].keys():
      if len(apps[app][meth])==0:
        x = {"f": getattr(mod, meth)}
        x["args"] = x["f"].__code__.co_varnames
        d = x["f"].__defaults__
        d = [] if d==None else d
        x["kwargs"] = dict(zip(x["args"][-len(d):],d))
        x["args"] = x["args"][:-len(d)]
        apps[app][meth] = x

  class ftws(http.server.BaseHTTPRequestHandler):
    def ww(s, txt):
      s.wfile.write(bytes(txt, "utf-8"))

    def do_GET(s):
      s.send_response(200)

      if s.path=="/":      
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.ww("<html><head><title>Frank's Terrible WebUI</title></head><body>")
        s.ww(f"<p>Yo.</p><p>The files are:<br/>{files}</p>")
        s.ww(f"<p>The apps are:<br/>{json.dumps(apps, default=lambda x : '', indent=2)}</p>")
        s.ww(f"<p>path is {s.path}</p>")
        s.ww("</body></html>")
      elif s.path=="/ftw/apps":
        s.send_header("Content-type", "application/json")
        s.end_headers()
        s.ww(json.dumps(apps, default=lambda x : '', indent=2))
      else:
        path = s.path.split("/")[1:]
        if (path[0]=="do" 
            and path[1] in apps 
            and path[2] in apps[path[1]]):
          s.send_header("Content-type", "application/json")
          s.end_headers()
          s.ww(json.dumps(apps[path[1]][path[2]]["f"](), indent=2))

  print(f"Frank's Terrible WebUI found {len(apps.keys())} apps.\nPress Ctrl+C to exit.")
  http.server.HTTPServer(('', 8000), ftws).serve_forever()
