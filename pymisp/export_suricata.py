#!/usr/bin/env python3
import os
import pymisp
import argparse
import urllib3

# this is only required because we are using a local instance with a self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read the connection details from environment variables (see tutorial step 1.7.3).
MISP_URL = os.getenv("MISP_URL", "https://192.168.56.30")
MISP_KEY = os.getenv("MISP_KEY")
if not MISP_KEY:
    raise SystemExit(
        "Please set the MISP_KEY environment variable, e.g.:\n"
        '  export MISP_KEY="your-api-key-here"'
    )

misp = pymisp.PyMISP(MISP_URL, MISP_KEY, ssl=False)  # ssl=False: self-signed lab cert

def get_misp_iocs(output_file):
    ips = misp.direct_call(
        "/attributes/restSearch",
        {
            "type": ["ip-src", "ip-dst", "ip"],  # Filter for the ip attributes
            "tags": "suricata:ingest", # Filter for the `suricata:ingest` tag
            "to_ids": True,
            "returnFormat": "csv",  # Request the response in CSV format
            "requested_attributes": [
                "value"
            ],  # Only request the 'value' field (IP addresses)
            "headerless": True,  # No CSV headers
        },
    )

    # strip quotes and remove duplicates
    ips = set([ip.strip('"') for ip in ips.split("\n") if ip])

    # write file to disk
    with open(output_file, "w+") as file:
        file.writelines("\n".join(ips))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Output ip list dataset file")
    parser.add_argument("output_file", help="Path to output file")
    args = parser.parse_args()

    get_misp_iocs(args.output_file)