---
marp: true
theme: circl
paginate: true
footer: "AI & MCP"
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

![CIRCL](images/circl-logo.png)

# AI & MCP

## MISP Integration Workshop

- Why MCP for MISP
- Configure misp-mcp
- Available queries
- Hands-on

---

# AI: MCP servers

**Bring MISP data to LLM assistants over the Model Context Protocol.**

- **misp-mcp** — a server exposing MISP as read-only tools an AI can call.
- The assistant turns a natural-language question into the right MISP query.
- **Read-only** — the assistant can search and read, never modify.

> AI accelerates the analyst — it does not replace `to_ids` discipline.

---

# Configure misp-mcp

**Point the server at your MISP instance.**

- Install: `pip install misp-mcp`
- Set `MISP_URL` and `MISP_API_KEY`.
- Use `MISP_VERIFYCERT=false` for the lab's self-signed cert.
- Register it with your MCP client — Claude Desktop / Claude Code.

> Access is read-only — a scoped API key is enough.

---

# Client config

**Register the server in your MCP client (e.g. `mcp.json`).**

```json
{
  "mcpServers": {
    "misp": {
      "command": "misp-mcp",
      "env": {
        "MISP_URL": "https://192.168.56.30",
        "MISP_API_KEY": "your-api-key",
        "MISP_VERIFYCERT": "false"
      }
    }
  }
}
```

---

# What you can ask it

**The server exposes read-only MISP queries as tools.**

- **Events & attributes** — `search_events`, `search_attributes`, `get_event`
- **Tags & taxonomies** — `search_tags`, `list_taxonomies`, `get_taxonomy`
- **Galaxies** — `search_galaxies` (ATT&CK, threat actors, malware)
- **Feeds** — `search_feeds`

> The assistant picks the right tool — you just ask the question.

---

<!-- _class: section -->
<!-- _footer: "" -->

# Hands-on

---

# Hands-on: example queries

**Ask MISP in natural language.**

- "Any events mentioning `185.194.93.14`?"
- "Show attributes tagged `tlp:clear` added this week."
- "What ATT&CK techniques relate to this threat actor?"
- "Summarise event 1234 and list its IOCs."
- "Which feeds are enabled?"

---

<!-- _class: standout -->
<!-- _footer: "" -->

# Questions?
