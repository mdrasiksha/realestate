from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routes import leads, properties, webhook

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(properties.router, prefix="/properties", tags=["Properties"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])


@app.get("/")
def home():
    return {"message": "Real Estate CRM running 🚀"}
