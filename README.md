\# LeadFlow Agent 🔔



\*\*Never lose another lead to a slow reply.\*\*



LeadFlow Agent is an AI-powered lead management agent that lives inside Slack.

Built for appointment-based small businesses (salons, clinics, physios, trades)

that lose revenue every day to forgotten follow-ups.



\## What it does



\- \*\*Natural language control\*\* — talk to it like a colleague: \*"add a lead: Tom, 085 999 8877, plumbing quote"\* or \*"what leads are still new?"\*

\- \*\*AI lead qualification\*\* — every new lead is analysed (priority + reasoning) and a warm, professional reply is drafted for staff

\- \*\*Autonomous follow-up reminders\*\* — the agent monitors the database and proactively nags the team about leads left waiting, until someone acts

\- \*\*Slash commands\*\* — `/newlead`, `/leads`, `/updatelead`, `/assignlead` for quick structured actions



\## Architecture



Slack (Socket Mode) ⇄ Bolt app (Python) ⇄ Agentic loop (Qwen via OpenAI-compatible API) ⇄ \*\*MCP server\*\* (FastMCP) ⇄ SQLite



The lead database is exposed exclusively through an \*\*MCP (Model Context Protocol) server\*\*

with four tools: `add\_lead`, `get\_open\_leads`, `update\_lead\_status`, `assign\_lead`.

The AI agent discovers and calls these tools autonomously — no hardcoded routing.



\## Stack



\- Python 3, Slack Bolt (Socket Mode)

\- MCP via FastMCP (`mcp\[cli]`)

\- Qwen (qwen-plus) on Alibaba Cloud Model Studio

\- SQLite, APScheduler



\## Run it



1\. `pip install -r requirements.txt`

2\. Create `.env`:



SLACK\_BOT\_TOKEN=xoxb-...

SLACK\_APP\_TOKEN=xapp-...

DASHSCOPE\_API\_KEY=sk-...



3\. `python app.py`



\## Built by



Blessing Fortune Kwomo — 3F Digitals, Limerick, Ireland

