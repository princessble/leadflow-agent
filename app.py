import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import database
import ai_brain
import agent
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()
database.init_db()
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def handle_mention(event, say):
    user = event["user"]
    # Remove the bot mention from the text
    text = event.get("text", "")
    cleaned = " ".join(w for w in text.split() if not w.startswith("<@")).strip()
    if not cleaned:
        say(f"Hello <@{user}>! 👋 Ask me anything about your leads — e.g. *'show me new leads'* or *'mark lead 3 as booked'*.")
        return
    say("🤔 On it...")
    try:
        answer = agent.ask_agent(cleaned)
        say(answer)
    except Exception as e:
        say(f"⚠️ Something went wrong: {e}")
@app.command("/newlead")
def handle_newlead(ack, command, respond):
    ack()
    text = command.get("text", "").strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 3:
        respond("⚠️ Format: `/newlead name | phone or email | service`\nExample: `/newlead Mary O'Brien | 087 123 4567 | physio appointment`")
        return
    name, contact, service = parts[0], parts[1], parts[2]
    lead_id = database.add_lead(name, contact, service)
    respond(f"✅ Lead #{lead_id} added: *{name}* ({contact}) — interested in _{service}_.\n🧠 Analysing lead...")
    try:
        analysis = ai_brain.qualify_lead(name, contact, service)
        respond(f"🧠 *AI Analysis for Lead #{lead_id}:*\n{analysis}")
    except Exception as e:
        respond(f"⚠️ AI analysis unavailable: {e}")

@app.command("/leads")
def handle_leads(ack, respond):
    ack()
    leads = database.get_open_leads()
    if not leads:
        respond("🎉 No open leads — inbox zero!")
        return
    lines = ["*📋 Open Leads:*"]
    for lead in leads:
        lead_id, name, contact, service, status = lead
        lines.append(f"• *#{lead_id} {name}* ({contact}) — _{service}_ — status: `{status}`")
    respond("\n".join(lines))

@app.command("/updatelead")
def handle_updatelead(ack, command, respond):
    ack()
    parts = [p.strip() for p in command.get("text", "").split("|")]
    if len(parts) < 2:
        respond("⚠️ Format: `/updatelead lead ID | new status`\nExample: `/updatelead 3 | contacted`\nStatuses: new, contacted, booked, closed")
        return
    lead_id, status = parts[0], parts[1].lower()
    if database.update_status(lead_id, status):
        respond(f"🔄 Lead #{lead_id} updated to `{status}`")
    else:
        respond(f"❌ Couldn't find lead #{lead_id}")

@app.command("/assignlead")
def handle_assignlead(ack, command, respond):
    ack()
    parts = [p.strip() for p in command.get("text", "").split("|")]
    if len(parts) < 2:
        respond("⚠️ Format: `/assignlead lead ID | @person`\nExample: `/assignlead 3 | @blessing`")
        return
    lead_id, person = parts[0], parts[1]
    if database.assign_lead(lead_id, person):
        respond(f"👤 Lead #{lead_id} assigned to {person} — they're on it!")
    else:
        respond(f"❌ Couldn't find lead #{lead_id}")

REMINDER_CHANNEL = "#general"
STALE_AFTER_MINUTES = 3      # demo setting - use 60+ in real life
CHECK_EVERY_MINUTES = 2      # how often to check

def check_stale_leads():
    stale = database.get_stale_leads(minutes=STALE_AFTER_MINUTES)
    if not stale:
        return
    lines = ["🔔 *Follow-up reminder!* These leads are still waiting for contact:"]
    for lead_id, name, contact, service, age in stale:
        lines.append(f"• *#{lead_id} {name}* ({contact}) — _{service}_ — waiting *{age} min*")
    lines.append("_Reply to them before they book elsewhere! Use_ `/updatelead ID | contacted` _when done._")
    app.client.chat_postMessage(channel=REMINDER_CHANNEL, text="\n".join(lines))

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_stale_leads, "interval", minutes=CHECK_EVERY_MINUTES)
    scheduler.start()
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("⚡ LeadFlow Agent is running! (reminders every "
          f"{CHECK_EVERY_MINUTES} min, nagging after {STALE_AFTER_MINUTES} min)")
    handler.start()