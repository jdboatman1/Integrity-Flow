from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import secrets
from motor.motor_asyncio import AsyncIOMotorClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = FastAPI(title="Integrity Flow Customer Portal API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = mongo_client.integrity_flow

# ERPNext Configuration
ERPNEXT_URL = os.getenv("ERPNEXT_URL")
ERPNEXT_API_KEY = os.getenv("ERPNEXT_API_KEY")
ERPNEXT_API_SECRET = os.getenv("ERPNEXT_API_SECRET")

# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_NAME = os.getenv("FROM_NAME")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Pydantic Models
class MagicLinkRequest(BaseModel):
    email: EmailStr

class CustomerInfo(BaseModel):
    customer_name: str
    email: EmailStr
    mobile_no: Optional[str] = None
    address: Optional[str] = None

class ScheduleRequest(BaseModel):
    customer_email: EmailStr
    service_type: str
    preferred_date: str
    preferred_time: str
    description: str

# Helper Functions
async def send_magic_link(email: str, token: str):
    """Send magic link email"""
    magic_link = f"{FRONTEND_URL}/auth/verify?token={token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f4f7f9; padding: 30px; border-radius: 10px;">
                <h2 style="color: #1b7abf;">🔐 Login to Your Customer Portal</h2>
                <p>Click the button below to securely access your AAA Irrigation Service portal:</p>
                <a href="{magic_link}" style="display: inline-block; padding: 15px 30px; background: #1b7abf; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">Access Portal</a>
                <p style="color: #666; font-size: 14px;">This link expires in 30 minutes.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px; text-align: center;">Powered by Boatman Systems™</p>
            </div>
        </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your Portal Login Link - AAA Irrigation Service'
    msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg['To'] = email
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send magic link")

async def get_erpnext_customer(email: str):
    """Fetch customer from ERPNext by email"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ERPNEXT_URL}/api/resource/Customer",
                params={"filters": f'[["email_id", "=", "{email}"]]'},
                headers={
                    "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    return data["data"][0]
            return None
        except Exception as e:
            print(f"Error fetching customer: {e}")
            return None

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Integrity Flow Customer Portal API - Powered by Boatman Systems™"}

@app.post("/api/auth/request-magic-link")
async def request_magic_link(request: MagicLinkRequest, background_tasks: BackgroundTasks):
    """
    Send magic link to customer email
    """
    # Check if customer exists in ERPNext
    customer = await get_erpnext_customer(request.email)
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="No customer account found with this email. Please contact us to create an account."
        )
    
    # Generate magic link token
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=30)
    
    # Store token in MongoDB
    await db.magic_tokens.insert_one({
        "token": token,
        "email": request.email,
        "customer_id": customer.get("name"),
        "expiry": expiry,
        "used": False
    })
    
    # Send magic link email
    background_tasks.add_task(send_magic_link, request.email, token)
    
    return {"message": "Magic link sent! Check your email."}

@app.get("/api/auth/verify")
async def verify_magic_link(token: str):
    """
    Verify magic link token and return customer data
    """
    # Find token in database
    token_doc = await db.magic_tokens.find_one({"token": token})
    
    if not token_doc:
        raise HTTPException(status_code=404, detail="Invalid token")
    
    if token_doc["used"]:
        raise HTTPException(status_code=400, detail="Token already used")
    
    if datetime.utcnow() > token_doc["expiry"]:
        raise HTTPException(status_code=400, detail="Token expired")
    
    # Mark token as used
    await db.magic_tokens.update_one(
        {"token": token},
        {"$set": {"used": True}}
    )
    
    # Get customer data from ERPNext
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ERPNEXT_URL}/api/resource/Customer/{token_doc['customer_id']}",
            headers={
                "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}"
            }
        )
        
        if response.status_code == 200:
            customer_data = response.json()["data"]
            return {
                "customer": {
                    "id": customer_data.get("name"),
                    "name": customer_data.get("customer_name"),
                    "email": customer_data.get("email_id"),
                    "phone": customer_data.get("mobile_no"),
                    "address": customer_data.get("primary_address")
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch customer data")

@app.get("/api/customer/{customer_id}/quotations")
async def get_customer_quotations(customer_id: str):
    """
    Get all quotations for a customer
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ERPNEXT_URL}/api/resource/Quotation",
            params={"filters": f'[["party_name", "=", "{customer_id}"]]', "fields": '["*"]'},
            headers={
                "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch quotations")

@app.get("/api/customer/{customer_id}/invoices")
async def get_customer_invoices(customer_id: str):
    """
    Get all invoices for a customer
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ERPNEXT_URL}/api/resource/Sales Invoice",
            params={"filters": f'[["customer", "=", "{customer_id}"]]', "fields": '["*"]'},
            headers={
                "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch invoices")

@app.post("/api/schedule-appointment")
async def schedule_appointment(request: ScheduleRequest):
    """
    Create a new quotation/appointment request
    """
    # Get customer by email
    customer = await get_erpnext_customer(request.customer_email)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create quotation in ERPNext
    quotation_data = {
        "doctype": "Quotation",
        "quotation_to": "Customer",
        "party_name": customer.get("name"),
        "custom_scheduled_date": request.preferred_date,
        "custom_scheduled_time": request.preferred_time,
        "custom_service_description": f"{request.service_type}\n\n{request.description}",
        "transaction_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ERPNEXT_URL}/api/resource/Quotation",
            json=quotation_data,
            headers={
                "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}"
            }
        )
        
        if response.status_code in [200, 201]:
            return {"message": "Appointment scheduled successfully", "data": response.json()}
        else:
            raise HTTPException(status_code=500, detail="Failed to schedule appointment")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)