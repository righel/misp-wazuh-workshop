##!/usr/bin/env python3
import os
import pymisp
import urllib3

# this is only required because we are using a local instance with a self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set these via environment variables, e.g.:
#   export MISP_URL="https://192.168.56.30"   # defaults to the lab VM IP
#   export MISP_KEY="your-api-key-here"        # required, no default
MISP_URL = os.getenv("MISP_URL", "https://192.168.56.30")
MISP_KEY = os.getenv("MISP_KEY")
if not MISP_KEY:
    raise SystemExit(
        "Please set the MISP_KEY environment variable, e.g.:\n"
        '  export MISP_KEY="your-api-key-here"'
    )

misp = pymisp.PyMISP(
    MISP_URL,
    MISP_KEY,
    ssl=False # Disable SSL verification
)

# /events/restSearch
events = misp.search(
    "events",
    # tags=["tlp:white", "tlp:clear"],
    limit=10,
    pythonify=True,
)
for event in events:
    print(f"Event UUID: {event.uuid}")
    print(f"Info: {event.info}")
    print(f"Date: {event.date}")
    print("" + "-" * 40)