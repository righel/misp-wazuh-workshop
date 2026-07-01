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

# IPs CSV - using direct API call to /attributes/restSearch endpoint
# Paginate through all results, fetching one page at a time until a page
# comes back empty.
page_size = 1000
page = 1
all_ips = []

while True:
    ips = misp.direct_call(
        "/attributes/restSearch",
        {
            "type": ["ip-src", "ip-dst", "ip"],  # Filter for the ip attributes
            # tags=["tlp:white", "tlp:clear"],
            "to_ids": True,
            "returnFormat": "csv",  # Request the response in CSV format
            "requested_attributes": [
                "value"
            ],  # Only request the 'value' field (IP addresses)
            "headerless": True,  # No CSV headers
            "limit": page_size,  # Number of results per page
            "page": page,  # Current page number
        },
    )

    # CSV return format gives us a string; split into non-empty lines.
    lines = [line for line in ips.splitlines() if line.strip()]
    if not lines:
        break  # No more results

    all_ips.extend(lines)

    if len(lines) < page_size:
        break  # Last (partial) page reached

    page += 1

print("\n".join(all_ips))