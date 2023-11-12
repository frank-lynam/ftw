import sys, os, http.server, json, urllib.parse
import uuid, threading

# Some globals because who cares, it's fine
apps={}
tasks={}

class ftws(http.server.BaseHTTPRequestHandler):
  # This is the webserver

  def ww(s, txt, code=200, content="application/json"):
    # A simple little wrapper to make responses easier

    s.send_response(code)
    s.send_header("Content-type", content)
    s.end_headers()
    s.wfile.write(bytes(txt, "utf-8"))

  def do_GET(s):
    # Handle gets

    if s.path=="/":
      # Personally, I *like* embedding code in code
      #   You should be grateful I didn't base64 encode it

      s.ww("""
<html><head><title>Frank's Terrible WebUI</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    body { background: #000201; color: #cde; font-size: 3em;
      text-align: center; }
    .bbox { display: flex; gap: .75em; margin: 0.5em;
      justify-content: center; flex-flow: column wrap; 
      min-height: 85vh; align-items: center; 
      transition: ease-out .2s; position: fixed;
      top: 0; left: 0; width: 100vw; 
      transform: translate(0, -100vh); } 
    .btn { padding: .75em 1em; border: 2px solid #cde; 
      user-select: none; text-align: center; 
      border-radius: 0.2em; transition: ease-in-out .05s;
      filter: drop-shadow(0.2em 0.2em 0.1em #666); } 
    .btn:hover,focus { filter: brightness(1.75) 
      drop-shadow(0.1em 0.1em 0.1em #666); 
      transform: translate(0.1em, 0.1em); }
    input { font-size: 1em; width: 5em; }
  </style>
</head><body>
  <div id="ftw_div_a" class="bbox"></div>
  <div id="ftw_div_b" class="bbox"></div>
</body>
<script>
  // Gives me a nice way to point at the divs
  let a = document.getElementById("ftw_div_a");
  let b = document.getElementById("ftw_div_b");
  let c = (n=0)=>[a,b][(state.length+n)%2];

  // Nice formatting for labels
  let entitle = (t)=>` ${t}`.replaceAll("_"," ").split("")
    .map(x=>x==x.toLowerCase()?x:" "+x)
    .reduce((a,b)=>a.at(-1)==" "?a+b.toUpperCase():a+b)
    .replaceAll("  "," ").trim()

  // Stores button info
  let state = [], api={};

  // Pretty, but consistent, prng colors
  let colory = s=>`hsl(${s.split('').map(x=>x.charCodeAt(0))
    .reduce((a,b)=>2*a+b)%360},80%,20%)`;

  // Makes the buttons
  let pop = ()=>{c().innerHTML="";
    if (state.length>0) {c().innerHTML+='<div class="btn" '
      + 'style="background: #222; margin-bottom: 1em;" '
      + 'onclick="state.pop(); swipe(true);">Back</div>'}
    if (state.length<2) {c().innerHTML+=
      Object.keys(state.reduce((a,b)=>a[b],api))
      .map(x=>`<div onclick="goto('${x}')" class="btn" `
      + `style="background: ${colory(x)}">${entitle(x)}`
      + `</div>`).join("\\n")}
    else if (state.length==2) {c().innerHTML+=
      Object.entries(state.reduce((a,b)=>a[b],api).ui)
      .map(a=>`<div><label for="${a[0]}">${entitle(a[0])}: `
      + `<`+ ("_tag" in a[1] ? a[1]._tag : "input")
      + ` id="${a[0]}"${Object.entries(a[1])
        .map(c=>" "+c[0]+"='"+c[1]+"'").join("")}>`
      + ("_text" in a[1] ? a[1]._text : "")
      + `</` + ("_tag" in a[1] ? a[1]._tag : "input")
      + `></label></div>`).join("\\n")
      + '<div class="btn" style="background: #253; '
      + 'margin-top: 1em;" onclick="fire()">Go</div>'}
    else {c().innerHTML+=state.at(-1)
      .map(x=>"<" + ("_tag" in x ? x._tag : "div") + " "
      + Object.entries(x).filter(y=>!y[0].startsWith("_"))
        .map(y=>y[0]+'="'+y[1]+'"').join(" ") + ">"
      + ("_text" in x ? x._text : "") + "</" 
      + ("_tag" in x ? x._tag : "div") + ">").join("\\n")}
  }

  // Do a function, then show the result
  let fire = ()=>fetch(`/do/${state[0]}/${state[1]}?ftw=true&`
    + Object.keys(api[state[0]][state[1]].ui)
      .filter(x=>!x.startsWith("FTW "))
      .map(x=>x+"="+encodeURIComponent(document
        .getElementById(x).value)).join("&"))
    .then(r=>r.json()).then(r=>{state.push(r); swipe()});

  // Go to the next api layer
  let goto = (b)=>{ state.push(b); swipe(); }

  // Animate buttons sliding in and out
  let swipe = (back=false)=>{
    c(1).style.transform=`translate(${back?0:"-100vw"}, `
      + `${back?"-100vh":0})`;
    c().style.transition="0s";
    c().style.transform=`translate(${back?"-100vw":0}, `
      + `${back?0:"-100vh"})`;
    pop();
    setTimeout(()=>{
      c().style.transition="ease-out .2s";
      c().style.transform="translate(0, 0)";
    },10);
  }

  // Initialize the page
  fetch("/ftw/api").then(r=>r.json())
    .then(r=>{api=r; swipe();})
</script>
</html>
""", content="text/html")
    elif s.path=="/ftw/api":
      # Gives my custom api schema

      s.ww(json.dumps(apps, default=lambda x : '', indent=2))
    elif s.path=="/favicon.svg":
      # My totally sweet logo

      s.ww('<svg xmlns="http://www.w3.org/2000/svg"><polygon '
        + 'points="30,30 60,30 35,40 50,40 35,50 30,80 45,80 '
        + '42,55 35,50 55,50 47,55 45,80 60,80 55,40 62,70 '
        + '65,50 67,70 75,40 70,80 65,75 60,80 30,80" />'
        + '</svg>', content="image/svg+xml")
    else:
      # Try to do api things if we can

      path = s.path.split("?")[0].split("/")[1:]
      payload = ({x:urllib.parse.unquote(y) for x,y in 
        [z.split("=") for z in 
          s.path.split("?")[-1].split("&") if z !=""]} 
        if "?" in s.path and s.path[-1]!="?" else {})
      s.deal_with_it(path, payload)    

  def deal_with_it(s, path, payload):
    # This figures out how to respond

    print("Path: " + json.dumps(path))
    print("Payload: " + json.dumps(payload))
    response = teapot()
    if (path[1] in apps and path[2] in apps[path[1]]):
      if (path[0]=="do"): 
        response = {"txt": json.dumps(do(
          apps[path[1]][path[2]]["f"], payload), indent=2)}
      elif (path[0]=="q"): 
        response = {"txt": json.dumps(q(
          apps[path[1]][path[2]]["f"], payload), indent=2)}
      elif (path[0]=="r" and "id" in payload): 
        response = r(payload["id"])

    print("Response: " + json.dumps(response))
    s.ww(**response)

  def do_POST(s):
    # This handles posts

    path = s.path.split("/")[1:]
    payload = (json.loads(s.rfile.read(int(
      s.headers.get("content-length"))).decode()) 
      if s.headers.get("content-length") else {})
    s.deal_with_it(path, payload)

def ftw(low,__get_low=False):
  # This is my fancy wrapper that lets me do the
  #   get low behavior to get kwargs

  def omw(f):
    def w(*args, **kwargs):
      if "__get_low" in kwargs:
        return low
      return f(*args, **kwargs)
    return w
  return omw

def ftfy(p="."):
  # Reads python files to turn them into an api spec

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
      return {x.split("def ")[1].split("(")[0].strip():
              [None] for x in t.split("@ftw")[1:]}
    return {x.split("(")[0].strip():[] 
            for x in t.split("def ")[1:]}

  # Oooh, spooky scary global variable!
  global apps
  apps = {f[:-3]:methods(f) for f in files}
  apps = {k:v for k,v in apps.items() if v!=None}

  # Populate the api spec with the stuff I want
  for app in apps.keys():
    mod=__import__(app)
    for meth in apps[app].keys():
      x = {"f": getattr(mod, meth)}
      if len(apps[app][meth])==0:
        x["args"] = x["f"].__code__.co_varnames
        d = x["f"].__defaults__
        d = [] if d==None else d
        x["kwargs"] = dict(zip(x["args"][-len(d):],d))
        x["args"] = x["args"][:-len(d)]
        x["ui"] = {"FTW Function":{"_tag":"span",
                                   "_text":app+"."+meth}}
        x["ui"].update({a:{} for a in x["args"]})
        x["ui"].update({a:{"value":b} 
                        for a,b in x["kwargs"].items()})
      else:
        x["ui"] = x["f"](__get_low=True)
      apps[app][meth] = x
      
  # Gives nice Ctrl+C behavior
  try:
    start(apps)
  except KeyboardInterrupt:
    print("\rBuh-bye!")

def do(f, kwargs):
  # Actually run functions, then wrap their result
  #   in a component

  r = f(**{k:v for k,v in kwargs.items() 
           if not k.lower().startswith("ftw")})
  if ("ftw" in kwargs and kwargs["ftw"] 
      and (not isinstance(r, list) 
      or any([not isinstance(x, dict) for x in r]))):
    r = [{"style":"white-space:pre", "_text":r}]
  print("Task result: " + json.dumps(r))
  return r

def q(f, kwargs):
  # Spin off tasks in a thread and return a ref id

  id = str(uuid.uuid4())[:8]
  tasks[id] = {"thread": threading.Thread(target=qw, 
                  args=(f, kwargs, id)),
               "name": f.__name__, "kwargs": kwargs}
  tasks[id]["thread"].start()
  return id

def qw(f, kwargs, id):
  # A wrapper to turn threads in responses

  tasks[id]["result"] = {"txt": json.dumps(do(f, kwargs),
                                           indent=2)}

def r(id):
  # Tries to return results if available

  if id in tasks and "result" in tasks[id]:
    return tasks[id]["result"]
  return teapot()

def teapot():
  # For when I don't know what to do

  return {"txt":"I'm a little teapot\n", "code":418, 
          "content":"text/plain"}

def start(appspec={}):
  # Starts the server

  apps=appspec
  print(f"Frank's Terrible WebUI found {len(apps.keys())} "
    + "apps.\nPress Ctrl+C to exit.")
  http.server.HTTPServer(('', 8000), ftws).serve_forever()

if __name__=="__main__":
  # Starts a server based on command line args
  #   if any are given

  ftfy(sys.argv[1]) if len(sys.argv) > 1 else ftfy()
