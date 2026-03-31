from fastapi import APIRouter

from ..schemas import WebhookPayload

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/")
def receive_webhook(payload: WebhookPayload):
    return {
        "received": True,
        "source": payload.source,
        "event": payload.event,
    }
