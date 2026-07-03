from mcp.server.fastmcp import FastMCP
import database

database.init_db()

mcp = FastMCP("LeadFlow")

@mcp.tool()
def add_lead(name: str, contact: str, service: str) -> str:
    """Add a new lead to the LeadFlow database.
    name: the lead's full name
    contact: phone number or email
    service: what service they are interested in
    """
    lead_id = database.add_lead(name, contact, service)
    return f"Lead #{lead_id} added: {name} ({contact}) - {service}"

@mcp.tool()
def get_open_leads() -> str:
    """List all open (not closed) leads with their id, name, contact, service and status."""
    leads = database.get_open_leads()
    if not leads:
        return "No open leads."
    lines = []
    for lead in leads:
        lead_id, name, contact, service, status = lead
        lines.append(f"#{lead_id} {name} ({contact}) - {service} - status: {status}")
    return "\n".join(lines)

@mcp.tool()
def update_lead_status(lead_id: int, status: str) -> str:
    """Update a lead's status. Valid statuses: new, contacted, booked, closed."""
    if database.update_status(lead_id, status):
        return f"Lead #{lead_id} updated to {status}"
    return f"Lead #{lead_id} not found"

@mcp.tool()
def assign_lead(lead_id: int, person: str) -> str:
    """Assign a lead to a team member by name or Slack handle."""
    if database.assign_lead(lead_id, person):
        return f"Lead #{lead_id} assigned to {person}"
    return f"Lead #{lead_id} not found"

if __name__ == "__main__":
    mcp.run()