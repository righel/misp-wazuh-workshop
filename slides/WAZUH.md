---
marp: true
theme: circl
paginate: true
footer: "MISP ↔ Wazuh Integration"
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

![CIRCL](images/circl-logo.png)

# MISP ↔ Wazuh Integration

## MISP Integration Workshop

- MISP → Wazuh (detection)
- The lookup pattern
- Tuning rules & decoders
- Rate-limiting & caching
- Hands-on

---

<!-- _class: section -->
<!-- _footer: "" -->

# MISP → Wazuh (detection)

---

# Enriching alerts with MISP

**A custom integration script that queries MISP for IOCs found in Wazuh events.**

- Wazuh calls an **integration script** on matching events.
- The script queries the **MISP REST API** for the extracted indicator.
- A hit turns a routine log line into an **intelligence-backed alert**.

> Wazuh sees the event; MISP says whether it matters.

---

# The lookup pattern

**Decode → extract → query → alert.**

- **Decode / extract** — Wazuh pulls an IOC from the log (hash, IP, domain).
- **Query** — the custom integration script hits the MISP REST API
  (`/attributes/restSearch`).
- **Alert** — a match generates a **high-severity** alert with MISP context.

> The same pattern works for hashes, IPs, and domains — only the extraction changes.

---

# Tuning rules & decoders

**Make MISP-matched events surface clearly.**

- Add a **dedicated rule** for the integration's output so matches stand out.
- Set an appropriate **alert level** so MISP hits rise above the noise.
- Enrich the alert with MISP fields (event id, tags, category) for the analyst.

> If a MISP match looks like every other alert, the integration adds no value.

---

# Rate-limiting & caching

**Don't hammer MISP on noisy logs.**

- Noisy sources can fire **thousands** of lookups per minute.
- **Cache** recent lookups (hit *and* miss) with a short TTL.
- **Rate-limit** or pre-filter which events trigger a lookup.
- Consider a **pull model** (local IOC list) for high-volume sources.

> Protect the MISP instance — a lookup storm degrades it for everyone.

---

<!-- _class: section -->
<!-- _footer: "" -->

# Hands-on

---

# Hands-on: see it fire

**Trigger a match and watch the pipeline end-to-end.**

1. **Trigger** a test event — a simulated malicious hash or DNS lookup.
2. **Watch** the MISP lookup fire from the integration script.
3. **See** the enriched, high-severity Wazuh alert with MISP context.

> One synthetic IOC proves the whole detection path works.

---

<!-- _class: standout -->
<!-- _footer: "" -->

# Questions?
