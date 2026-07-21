---
marp: true
theme: circl
paginate: true
footer: "Broadening the Ecosystem"
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

![CIRCL](images/circl-logo.png)

# Broadening the Ecosystem

## MISP Integration Workshop

- Suricata — network rules
- Zeek — Threat Intel module
- Dashboards
- MISP Workbench

---

# Suricata

**Export MISP IOCs as Suricata rules for network-layer detection.**

- Generate **Suricata rules** from MISP attributes (IPs, domains, URLs, hashes).
- Suricata matches them against live traffic at the network layer.
- Refresh the ruleset on a schedule so detection tracks the latest intel.

> Network-layer coverage — catch IOCs on the wire, not just on the host.

---

# Zeek

**Export MISP IOCs for the Zeek Threat Intel module.**

- Export attributes into the **Zeek Intel framework** format.
- Zeek's **Threat Intel module** watches traffic for those indicators.
- Matches land in `intel.log` with the surrounding connection context.

> Zeek adds rich context — who talked to the IOC, when, and how.

---

# Dashboards

**Visualize IOCs, trends, and more.**

- The new **dashboards** surface what's in MISP at a glance.
- Track **IOC volume**, feed activity, tags, and correlations over time.
- Spot trends and gaps that raw event lists hide.

> Dashboards turn the dataset into situational awareness.

---

<!-- _class: logo-br -->

# MISP Workbench

**Analyst-focused tool for threat intelligence.**

- A dedicated **analyst workspace** for exploring and correlating data.
- Pivot across events, attributes, and galaxies to build the picture.
- Complements the MISP ecosystem for deeper investigation.

> Built for the analyst's workflow, not just data entry.

![MISP Workbench](images/MISP-satellite_workbench-verti-color.png)

---

<!-- _class: section -->
<!-- _footer: "" -->

# Hands-on

---

# Hands-on: Zeek → MISP

**Pull model — Zeek fetches IOCs once and matches traffic itself.**

- Point Zeek at MISP so it loads the IOC set into memory.
- Ship Zeek's matches to Wazuh for alerting.
- Trigger a connection to a known-bad IP and watch the match.

> Full steps in the tutorial.

---

# Hands-on: Suricata → MISP

**Push model — a MISP lookup per network event.**

- Send Suricata's network events to Wazuh.
- Let the manager query MISP for each observed IP and domain.
- Trigger traffic to a known-bad indicator and watch the alert fire.

> Full steps in the tutorial.

---



<!-- _class: standout -->
<!-- _footer: "" -->

# Questions?
