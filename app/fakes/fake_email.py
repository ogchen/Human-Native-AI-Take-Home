import logging

from app.email import EmailClient

logger = logging.getLogger("uvicorn")


class FakeEmailClient(EmailClient):
    def send_email(self, recipient: str, title: str, body: str):
        email = f"""
Recipient: {recipient}
Title: {title}
Body:
{body}
        """
        logger.info(email)


def get_email_client():
    return FakeEmailClient()
