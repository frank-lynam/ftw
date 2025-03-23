# Frank's Terrible WebUI

A thing that turns python files into websites super easy. I made it on my phone just to see if I could.

## Use

Just run:

```bash
python3 ftw.py demo/
```

## Concept

 - [x] No non-standard dependencies
 - [x] Single python file
 - [x] Can just add decorator (or not!) and works
 - [ ] Can add static files if you want
 - [ ] Define custom widgets using "variable name": {"type": "range", "min": 1} etc
 - [ ] Handler for file uploads
 - [x] Rest api and web page
 - [x] Command line argument for path to code
 - [ ] Open API maybe?
 - [ ] Threaded tasks that run in the background
 - [x] All endpoints are immediate

### Basic Functionality

 - [x] Make inputs work
 - [ ] Allow custom index
 - [ ] Pass files as a file-like in memory
 - [ ] Add q async endpoint
 - [x] Break header stuff into new method
 - [ ] Store last used parameters in local storage
