# ==============================================================
# Frappe Server Script — Auto-Send Portal Invite on Schedule
# DocType:   Quotation
# Event:     after_insert
#
# Sends portal invite when a customer schedules from website
# ==============================================================

import frappe
from frappe import _

def send_schedule_portal_invite(doc):
    """Send portal invite when customer schedules appointment"""
    
    # Only send if this is a new quotation with scheduling info
    if not doc.custom_scheduled_date:
        return
    
    # Get customer
    try:
        customer = frappe.get_doc("Customer", doc.party_name)
    except:
        return
    
    # Check if customer has email
    if not customer.email_id:
        return
    
    # Check if we've already sent an invite (look for comment)
    existing_invites = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": "Customer",
            "reference_name": customer.name,
            "content": ["like", "%Portal invite email sent%"]
        }
    )
    
    # If invite already sent, skip
    if existing_invites:
        return
    
    # Portal URL
    portal_url = "https://portal.aaairrigationservice.com"
    
    # Format scheduled date/time
    scheduled_date = frappe.format(doc.custom_scheduled_date, {'fieldtype': 'Date'})
    scheduled_time = doc.custom_scheduled_time or "TBD"
    
    # Email HTML template
    email_content = f"""
    <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background: #f4f7f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1b7abf; font-size: 32px; font-weight: 900; font-style: italic; text-transform: uppercase;">
                        AAA Irrigation Service
                    </h1>
                </div>
                
                <div style="background: #d1fae5; border-left: 5px solid #059669; border-radius: 10px; padding: 20px; margin-bottom: 30px;">
                    <h2 style="color: #065f46; font-size: 20px; margin-bottom: 10px;">✅ Appointment Scheduled!</h2>
                    <p style="color: #047857; font-size: 16px; margin: 0;">
                        Thank you for scheduling with us, {customer.customer_name}!
                    </p>
                </div>
                
                <div style="background: #f7fafc; border-radius: 15px; padding: 25px; margin-bottom: 30px;">
                    <h3 style="color: #1b7abf; font-size: 18px; margin-bottom: 15px;">📅 Your Appointment Details:</h3>
                    <p style="color: #4a5568; font-size: 15px; line-height: 1.8; margin: 0;">
                        <strong>Date:</strong> {scheduled_date}<br>
                        <strong>Time:</strong> {scheduled_time}<br>
                        <strong>Estimate:</strong> #{doc.name}
                    </p>
                </div>
                
                <div style="background: linear-gradient(135deg, #1b7abf 0%, #059669 100%); border-radius: 15px; padding: 30px; margin-bottom: 30px;">
                    <h2 style="color: white; font-size: 22px; margin-bottom: 15px;">🌐 Access Your Customer Portal</h2>
                    <p style="color: white; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                        We've created a portal account for you! Track your appointment, view estimates, and manage your services online.
                    </p>
                    <div style="text-align: center;">
                        <a href="{portal_url}" style="display: inline-block; background: #ea580c; color: white; padding: 15px 40px; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 16px; text-transform: uppercase;">
                            Access Portal
                        </a>
                    </div>
                </div>
                
                <div style="background: #fef3c7; border-left: 5px solid #f59e0b; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #92400e; font-size: 16px; margin-bottom: 10px;">🔑 How to Log In:</h3>
                    <ol style="color: #78350f; font-size: 14px; line-height: 1.8; margin: 0; padding-left: 20px;">
                        <li>Visit the portal link above</li>
                        <li>Enter your email: <strong>{customer.email_id}</strong></li>
                        <li>We'll send you a secure magic link</li>
                        <li>Click the link in your email to access your portal</li>
                    </ol>
                </div>
                
                <div style="border-top: 2px solid #edf2f7; padding-top: 20px; text-align: center;">
                    <p style="color: #4a5568; font-size: 14px; margin-bottom: 10px;">
                        Questions about your appointment?
                    </p>
                    <p style="color: #1b7abf; font-size: 15px; font-weight: 700;">
                        📞 469-751-3567 | ✉️ info@aaairrigationservice.com
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #edf2f7;">
                    <p style="color: #a0aec0; font-size: 12px; font-style: italic; text-transform: uppercase; letter-spacing: 1px;">
                        Powered by Boatman Systems™
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
    try:
        # Send email
        frappe.sendmail(
            recipients=[customer.email_id],
            subject=f"Appointment Scheduled - Access Your Portal | AAA Irrigation",
            message=email_content,
            now=True
        )
        
        # Log success
        frappe.logger().info(f"Schedule + Portal invite sent to {customer.email_id} for quotation {doc.name}")
        
        # Add comment to customer record
        customer.add_comment(
            "Comment",
            f"Portal invite email sent to {customer.email_id} (triggered by quotation {doc.name}) - Powered by Boatman Systems™"
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send schedule portal invite: {str(e)}", "Portal Invite Error")

# ── Entry point called by Frappe ──
send_schedule_portal_invite(doc)