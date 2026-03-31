from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from .database import SessionLocal
from . import models

def check_followups():
    db = SessionLocal()
    today = date.today()

    leads = db.query(models.Lead).filter(
        models.Lead.follow_up_date != None
    ).all()

    for lead in leads:
        if lead.follow_up_date and lead.follow_up_date.date() == today:
            print(f"📞 Reminder: Call {lead.name} ({lead.phone}) today!")

    db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_followups, "interval", minutes=1)
    scheduler.start()