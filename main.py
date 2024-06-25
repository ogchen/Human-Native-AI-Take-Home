import uvicorn

from app.app import report_app
from app import db
from app import email
from app.fakes import fake_db
from app.fakes import fake_email

report_app.dependency_overrides[db.get_db] = fake_db.get_db
report_app.dependency_overrides[email.get_email_client] = fake_email.get_email_client

if __name__ == "__main__":
    uvicorn.run(report_app, host="0.0.0.0", port=8000)
