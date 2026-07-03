# MISP Integration Workshop — CIRCL

A hands-on lab that integrates two open-source security tools so that threat intelligence
drives detection:

* **[MISP](https://www.misp-project.org/)** — a Threat Intelligence Platform for
  collecting, storing and sharing Indicators of Compromise (IOCs) such as malicious IPs,
  domains and file hashes. Data is organised into _events_ (a report about an incident or
  campaign) made up of _attributes_ (the individual IOCs).
* **[Wazuh](https://wazuh.com/)** — an open-source security platform (SIEM/XDR). A central
  **Wazuh Manager** analyses telemetry shipped by lightweight **Wazuh Agents** on
  monitored hosts.

**Goal:** use MISP as a threat-intel source for Wazuh. As agents report file and network
activity, the Wazuh Manager queries MISP and raises an alert whenever an observed hash, IP
or domain matches a known IOC.

## Lab layout

The lab runs four VirtualBox VMs on a host-only network (`vboxnet0`):

```
192.168.56.1    the host itself (VirtualBox assigns this to vboxnet0)
192.168.56.10   wazuh-manager VM
192.168.56.20   wazuh-agent-01 VM
192.168.56.30   misp VM
192.168.56.50   flowintel VM
```

## Getting started

Download the pre-configured `.ova` file containing the 4 VMs **<TODO_INSERT_OVA_LINK>**.

The lab is distributed as a pre-configured `.ova` image, so you can go straight to the
walkthrough. If you'd rather build everything from scratch, follow the installation guide
instead.

| Document | What it covers |
|----------|----------------|
| **[TUTORIAL.md](TUTORIAL.md)** | The main walkthrough — start here. Explores MISP (orgs, tags, feeds, server sync, PyMISP scripting, enrichment modules) then deploys Wazuh and wires the two together. |
| **[INSTALLATION.md](INSTALLATION.md)** | How to build the lab from scratch: importing base VMs, host-only network, static IPs, and installing MISP (`misp-docker`) and Wazuh. Skip this if you import the `.ova`. |

## PyMISP example scripts

Small Python examples used in section 1.7 of the tutorial to query MISP through its REST
API. Each reads connection details from environment variables — set `MISP_KEY` (required)
and, if your instance isn't the lab default, `MISP_URL`:

```bash
export MISP_KEY="your-api-key-here"
# optional, defaults to https://192.168.56.30
export MISP_URL="https://192.168.56.30"
```

| Script | Purpose |
|--------|---------|
| [`pymisp/connect.py`](pymisp/connect.py) | Connection test — prints the MISP server version. |
| [`pymisp/get_events.py`](pymisp/get_events.py) | Lists recent events (UUID, info, date). |
| [`pymisp/get_iocs.py`](pymisp/get_iocs.py) | Fetches IP attributes flagged for detection (`to_ids=True`). |
| [`pymisp/get_iocs_csv.py`](pymisp/get_iocs_csv.py) | Exports all detection IPs as CSV, paginating through the API. |
| [`pymisp/export_suricata.py`](pymisp/export_suricata.py) | Exports IP IOCs tagged `suricata:ingest` as a plain list file for a Suricata `dataset` (see §4). |

See [TUTORIAL.md §1.7](TUTORIAL.md) for setup (virtualenv, `pip install pymisp`) and sample
output.

## Acknowledgments

Claude Opus 4.8 (Anthropic) assisted with the technical writing and helped articulate some
of the concepts in this workshop. All technical content was reviewed and validated by the
authors.
