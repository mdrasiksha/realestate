from fastapi import FastAPI
from .database import engine, Base
from .routes import leads, properties, webhook

app = FastAPI()

# Create tables
#Base.metadata.create_all(bind=engine)

app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(properties.router, prefix="/properties", tags=["Properties"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])


@app.get("/")
def home():
    return {"message": "Real Estate CRM running 🚀"}