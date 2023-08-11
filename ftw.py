import sys, os, http.server, json

apps={}

class ftws(http.server.BaseHTTPRequestHandler):
  def index(self):
    return ""

  def ww(s, txt, code=200, content="application/json"):
    s.send_response(code)
    s.send_header("Content-type", content)
    s.end_headers()
    s.wfile.write(bytes(txt, "utf-8"))

  def do_GET(s):
    if s.path=="/":      
      s.ww("""
<html><head><title>Frank's Terrible WebUI</title>
  <style>
    body { background: #000201; color: #cde; font-size: 3em; }
    .bbox { display: flex; gap: .75em; margin: 0.5em;
      justify-content: center; flex-flow: column wrap; 
      min-height: 85vh; align-items: center; 
      transition: ease-in-out .2s; } 
    .btn { padding: .75em 1em; border: 2px solid #cde; 
      user-select: none; text-align: center; } 
    .btn:hover,focus { filter: brightness(1.75); }
  </style>
</head><body>
  <div id="apps" class="bbox"></div>
  <div class="btn" style="position: fixed; bottom: .5em; left: .5em; background: #222;" onclick="state.pop(); swipe(true);">Back</div>
</body>
<script>
  let apps = document.getElementById("apps");
  let state = [], api={};
  let colory = s=>`hsl(${s.split('').map(x=>x.charCodeAt(0)).reduce((a,b)=>2*a+b)%360},80%,20%)`;
  let pop = ()=>apps.innerHTML=Object.keys(state.reduce((a,b)=>a[b],api)).map(x=>`<div onclick="goto('${x}')" class="btn" style="background: ${colory(x)}">${x}</div>`).join("\\n")
  let goto = (b)=>{ state.push(b); swipe(); }
  let swipe = (back=false)=>{
    apps.style.transform=`translate(${back?0:"-100vw"}, ${back?"-100vh":0})`;
    setTimeout(()=>{apps.innerHTML="";
      apps.style.transform=`translate(${back?"-100vw":0}, ${back?0:"-100vh"})`;
      setTimeout(()=>{pop();
        apps.style.transform="translate(0, 0)";
      }, 200);}, 200);}
  fetch("/ftw/api").then(r=>r.json())
    .then(r=>{api=r; swipe();})
</script>
</html>
""", content="text/html")
    elif s.path=="/ftw/api":
      s.ww(json.dumps(apps, default=lambda x : '', indent=2))
    else:
      path = s.path.split("/")[1:]
      if (path[0]=="do" 
          and path[1] in apps 
          and path[2] in apps[path[1]]):
        s.ww(json.dumps(apps[path[1]][path[2]]["f"](), indent=2))
      else:
        s.ww("I'm a little teapot\n", code=418, content="text/plain")

  def do_POST(s):
    path = s.path.split("/")[1:]
    if (path[0]=="do" 
        and path[1] in apps 
        and path[2] in apps[path[1]]):
      s.ww(json.dumps(apps[path[1]][path[2]]["f"](), indent=2))
    else:
      s.ww("I'm a little teapot\n", code=418, content="text/plain")

def ftw(f):
  def w(*args, **kwargs):
    return f(*args, **kwargs)
  return w

def ftfy(p="."):
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

  global apps
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
  start(apps)

def start(appspec={}):
  apps=appspec
  print(f"Frank's Terrible WebUI found {len(apps.keys())} apps.\nPress Ctrl+C to exit.")
  http.server.HTTPServer(('', 8000), ftws).serve_forever()

if __name__=="__main__":
  ftfy(sys.argv[1]) if len(sys.argv) > 1 else ftfy()
