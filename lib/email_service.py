import logging
import os
import smtplib
from email.message import EmailMessage
from typing import Optional, Tuple


class EmailService:
    """Simple SMTP email sender."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.server = os.getenv("SMTP_SERVER")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM") or self.username
        self.default_to = os.getenv("EMAIL_TO")

    def is_configured(self) -> bool:
        return all(
            [
                self.server,
                self.port,
                self.username,
                self.password,
                self.email_from,
            ]
        )

    def send_email(
        self,
        subject: str,
        body: str,
        to_email: Optional[str] = None,
    ) -> Tuple[bool, str]:
        if not self.is_configured():
            return False, "Email service not configured"

        recipient = to_email or self.default_to
        if not recipient:
            return False, "Recipient email is missing"

        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.starttls()
                if self.username and self.password:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)
            return True, "sent"
        except Exception as exc:
            self.logger.error("[EMAIL] Send failed: %s", exc)
            return False, "send failed"
