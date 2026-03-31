from fastapi import FastAPI

from .database import Base, engine
from .routes import leads, properties, webhook

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate CRM API")

app.include_router(leads.router)
app.include_router(properties.router)
app.include_router(webhook.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
