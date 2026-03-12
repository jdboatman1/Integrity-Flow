import frappe

def add_tech_schedule_shortcut():
    """Add Tech Schedule shortcut to the Selling workspace."""
    # Check if shortcut already exists
    existing = frappe.db.sql("""
        SELECT name FROM `tabWorkspace Shortcut`
        WHERE parent='Selling' AND label='Tech Schedule'
    """)
    if existing:
        print("Shortcut already exists, skipping")
        return

    # Get max idx for existing shortcuts
    max_idx = frappe.db.sql("""
        SELECT COALESCE(MAX(idx), 0) FROM `tabWorkspace Shortcut`
        WHERE parent='Selling'
    """)[0][0]

    now = frappe.utils.now()
    frappe.db.sql("""
        INSERT INTO `tabWorkspace Shortcut` (
            name, parent, parenttype, parentfield,
            type, label, icon, url, color, idx,
            owner, modified_by, creation, modified, docstatus
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        frappe.generate_hash("", 10),
        "Selling", "Workspace", "shortcuts",
        "URL", "Tech Schedule", "calendar", "/app/tech-schedule", "#1b7abf",
        max_idx + 1,
        "Administrator", "Administrator", now, now, 0
    ))
    frappe.db.commit()
    print("Added Tech Schedule shortcut to Selling workspace")
