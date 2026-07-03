# LeadFlow Agent

**Never lose another lead to a slow reply.**

LeadFlow Agent is an AI agent that lives inside Slack and looks after your leads so your team doesn't have to. Small appointment-based businesses — salons, clinics, physios, trades — lose customers every day for one simple reason: somebody meant to reply and forgot. This agent makes sure that never happens.

You talk to it in plain English. It captures leads, scores how urgent they are, drafts the follow-up reply, and keeps nagging the team about anyone left waiting — until someone actually acts.

---

## What it does

**Talk to it like a colleague.** No forms, no dashboards.

> `@LeadFlow Agent add a lead: Tom Byrne, 085 999 8877, wants a plumbing quote`
>
> `@LeadFlow Agent what leads are still new?`
>
> `@LeadFlow Agent mark lead 2 as closed`

**It thinks about every new lead.** The moment a lead comes in, the agent scores its priority and explains why:

> *Priority:* HIGH
> *Why:* Urgent physio request + direct phone number signals immediate need and high intent.
> *Suggested reply:* Hi Sarah, thanks for reaching out — we'd be happy to help with your back pain. Could we call you shortly to find a same-day slot?

**It never forgets.** A background scheduler watches the database. Any lead sitting uncontacted for too long gets flagged in the channel — automatically, with waiting times — until someone deals with it.

**Slash commands too**, for when you want structure over conversation: `/newlead`, `/leads`, `/updatelead`, `/assignlead`.

---

## Architecture

![LeadFlow Agent architecture](leadflow-architecture.png)

The interesting part is in the middle-right of that diagram: the lead database is never touched directly by the bot. Everything goes through an **MCP (Model Context Protocol) server** exposing four tools — `add_lead`, `get_open_leads`, `update_lead_status`, `assign_lead`.

When you mention the agent, your message goes to Qwen along with the MCP tool definitions. Qwen decides which tool fits, the MCP server executes it against SQLite, and the result flows back into Slack. There's no hardcoded routing — the model genuinely chooses. That's what makes it an agent rather than a chatbot with commands.

```
Slack (Socket Mode) ⇄ Bolt app ⇄ Agentic loop (Qwen) ⇄ MCP server ⇄ SQLite
```

---

## Stack

| Piece | Choice |
|---|---|
| Language | Python 3 |
| Slack framework | Bolt (Socket Mode — no public URL needed) |
| Agent tools | MCP via FastMCP |
| Reasoning | Qwen (`qwen-plus`) on Alibaba Cloud Model Studio |
| Storage | SQLite |
| Scheduling | APScheduler |
| Hosting | Alibaba Cloud ECS |

---

## Running it locally

1. Clone the repo and install dependencies:

```bash
   git clone https://github.com/princessble/leadflow-agent.git
   cd leadflow-agent
   pip install -r requirements.txt
```

2. Create a `.env` file in the project root:

```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_APP_TOKEN=xapp-your-token
   DASHSCOPE_API_KEY=sk-your-key
```

   The Slack tokens come from your app at [api.slack.com/apps](https://api.slack.com/apps) (bot token under OAuth & Permissions, app-level token under Basic Information). The DashScope key comes from Alibaba Cloud Model Studio.

3. Start the agent:

```bash
   python app.py
```

   You should see `⚡ LeadFlow Agent is running!` — then invite the bot to a channel and say hello.

---

## Project structure

```
app.py            Slack bot: events, slash commands, reminder engine
agent.py          Agentic loop: Qwen + MCP tool calling
mcp_server.py     MCP server exposing the four lead tools
ai_brain.py       Lead qualification and reply drafting
database.py       SQLite layer
test_mcp.py       Small client that verifies the MCP server works
```

---

## Author

**Blessing Fortune Kwomo** — [3F Digitals](https://www.3f-digitals.com), Limerick, Ireland.

Built for the Slack Agent Builder Challenge 2026.