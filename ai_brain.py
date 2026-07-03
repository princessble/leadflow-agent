import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

def qualify_lead(name, contact, service):
    """Ask Qwen to qualify a lead and suggest next action."""
    prompt = f"""You are LeadFlow Agent, a lead management assistant for a small appointment-based business (salon/clinic/physio/trades).

A new lead just arrived:
- Name: {name}
- Contact: {contact}
- Service interested in: {service}

In under 80 words, give:
1. Priority: HIGH/MEDIUM/LOW (appointment requests with phone numbers are usually HIGH - they want quick contact)
2. A one-line reason
3. A short, warm, professional draft reply the staff could send this lead (1-2 sentences)

Format exactly:
*Priority:* ...
*Why:* ...
*Suggested reply:* ..."""

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content