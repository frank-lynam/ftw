# Frank's Terrible WebUI

A thing that turns python files into websites super easy. I made it on my phone.

## Use

Just run:

```bash
python3 ftw.py demo/
```

## Concept

- No non-standard dependencies
- Single python file
- Can just add decorator (or not!) and works
- Can add static files if you want
- Define custom widgets using "variable name": {"type": "range", "min": 1} etc
- Handler for file uploads
- Rest api and web page
- Command line argument for path to code
- Open API maybe?
- Threaded tasks that run in the background
- All endpoints are immediate

# To do

- Make inputs work
- Allow custom index
- Pass files as a file-like in memory
- Add q endpoint
- Break header stuff into new method
- Store last used parameters in local storage
