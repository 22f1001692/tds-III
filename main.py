from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable open CORS access so the browser-based grader can verify it directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your assigned configuration
API_KEY = "ak_7skjesl49a8s7nvjpve77uxd"
# IMPORTANT: Update this before you deploy!
MY_EMAIL = "22f1001692@ds.study.iitm.ac.in" 

# --- Request Models ---
class Event(BaseModel):
    user: str
    amount: float
    ts: int

class AnalyticsPayload(BaseModel):
    events: List[Event]

# --- Authentication Dependency ---
async def verify_api_key(x_api_key: str = Header(default=None)):
    """Verifies the X-API-Key header. Raises 401 if missing or incorrect."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return x_api_key

# --- Analytics Endpoint ---
@app.post("/analytics")
async def process_analytics(payload: AnalyticsPayload, api_key: str = Depends(verify_api_key)):
    events = payload.events
    
    total_events = len(events)
    unique_users = set()
    total_revenue = 0.0
    user_revenue = {}
    
    for event in events:
        # Track unique users (regardless of amount)
        unique_users.add(event.user)
        
        # Only process revenue and top user logic for positive amounts
        if event.amount > 0:
            total_revenue += event.amount
            user_revenue[event.user] = user_revenue.get(event.user, 0.0) + event.amount
            
    # Find the user with the highest accumulated positive revenue
    # max() uses the dictionary values to determine the highest, then returns the key (username)
    top_user = max(user_revenue, key=user_revenue.get) if user_revenue else None
    
    return {
        "email": MY_EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users),
        "revenue": total_revenue,
        "top_user": top_user
    }
