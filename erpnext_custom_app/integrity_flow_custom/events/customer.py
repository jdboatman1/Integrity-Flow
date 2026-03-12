import frappe
from frappe import _

def send_portal_invite(doc, method):
    """
    Send portal invite email to new customer
    """
    # Check if customer has email
    if not doc.email_id:
        frappe.log_error(f"Customer {doc.name} created without email", "Portal Invite")
        return
    
    # Get portal URL from settings
    portal_url = frappe.db.get_single_value("Integrity Flow Settings", "portal_url") or "https://portal.aaairrigationservice.com"
    
    # Email HTML template with Boatman Systems™ branding
    email_content = f"""
    <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background: #f4f7f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1b7abf; font-size: 32px; font-weight: 900; font-style: italic; text-transform: uppercase; margin-bottom: 10px;">
                        AAA Irrigation Service
                    </h1>
                    <p style="color: #4a5568; font-size: 16px;">Welcome to Your Customer Portal</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #1b7abf 0%, #059669 100%); border-radius: 15px; padding: 30px; margin-bottom: 30px;">
                    <h2 style="color: white; font-size: 24px; margin-bottom: 15px;">Welcome, {doc.customer_name}!</h2>
                    <p style="color: white; font-size: 16px; line-height: 1.6;">
                        Your customer portal account has been created. Access your portal to:
                    </p>
                    <ul style="color: white; font-size: 15px; line-height: 1.8; margin-top: 15px;">
                        <li>View estimates and invoices</li>
                        <li>Schedule service appointments</li>
                        <li>Track job history</li>
                        <li>Pay invoices online</li>
                        <li>View your equipment details</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{portal_url}" style="display: inline-block; background: #ea580c; color: white; padding: 15px 40px; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 16px; text-transform: uppercase;">
                        Access Your Portal
                    </a>
                </div>
                
                <div style="background: #f7fafc; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #1b7abf; font-size: 18px; margin-bottom: 15px;">How to Log In:</h3>
                    <ol style="color: #4a5568; font-size: 15px; line-height: 1.8;">
                        <li>Visit <a href="{portal_url}" style="color: #1b7abf;">{portal_url}</a></li>
                        <li>Enter your email address: <strong>{doc.email_id}</strong></li>
                        <li>Click "Send Magic Link"</li>
                        <li>Check your email for the secure login link</li>
                    </ol>
                </div>
                
                <div style="border-top: 2px solid #edf2f7; padding-top: 20px; text-align: center;">
                    <p style="color: #4a5568; font-size: 14px; margin-bottom: 10px;">
                        Questions? Contact us:
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
            recipients=[doc.email_id],
            subject="Welcome to AAA Irrigation Service Customer Portal",
            message=email_content,
            delayed=False
        )
        
        # Add a comment to the customer record
        doc.add_comment(
            "Comment",
            f"Portal invite email sent to {doc.email_id} - Powered by Boatman Systems™"
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send portal invite to {doc.email_id}: {str(e)}", "Portal Invite Error")
