from fastapi import FastAPI
from .reminder import start_scheduler
from . import models
from .database import Base, engine
from .routes import auth, leads, properties, webhook
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.on_event("startup")
def start_app():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(properties.router, prefix="/properties", tags=["Properties"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])


@app.get("/")
def home():
    return {"message": "Real Estate CRM running 🚀"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
