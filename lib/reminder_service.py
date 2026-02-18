"""Birthday reminder service with email sending for Gift Genius"""

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import List, Optional, Tuple

from lib.recommender import GiftRecommender
from lib.types import GiftWizardState, PersonaReminder

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for handling birthday reminders and email sending"""

    def __init__(self, recommender: GiftRecommender, email_inbox: List[dict]):
        self.recommender = recommender
        self.email_inbox = email_inbox

        # SMTP configuration
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM") or self.smtp_username
        self.default_to = os.getenv("EMAIL_TO")

    def is_email_configured(self) -> bool:
        """Check if SMTP email is properly configured"""
        return all(
            [
                self.smtp_server,
                self.smtp_port,
                self.smtp_username,
                self.smtp_password,
                self.email_from,
            ]
        )

    def send_email(
        self,
        subject: str,
        body: str,
        to_email: Optional[str] = None,
        html_body: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Send email via SMTP"""
        if not self.is_email_configured():
            return False, "Email service not configured"

        recipient = to_email or self.default_to
        if not recipient:
            return False, "Recipient email is missing"

        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            assert self.smtp_server is not None  # Checked by is_email_configured()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                if self.smtp_username and self.smtp_password:
                    smtp.login(self.smtp_username, self.smtp_password)
                smtp.send_message(msg)
            return True, "sent"
        except Exception as exc:
            logger.error("[EMAIL] Send failed: %s", exc)
            return False, "send failed"

    def format_suggestions(self, persona: PersonaReminder) -> List[dict]:
        """Format gift suggestions for a persona"""
        try:
            wizard_state = GiftWizardState(
                occasion="Birthday",
                delivery_date=None,
                recipient_name=persona.name,
                recipient_loves=persona.loves or [],
                recipient_hates=persona.hates or [],
                recipient_allergies=persona.allergies or [],
                recipient_dietary=persona.dietary_restrictions or [],
                recipient_description=persona.description or None,
            )
            recommendations = self.recommender.get_recommendations(wizard_state)
            picks = [
                ("Best Match", recommendations.best_match),
                ("Safe Bet", recommendations.safe_bet),
                ("Something Unique", recommendations.unique),
            ]
            suggestions = []
            for label, rec in picks:
                if rec is None:
                    continue
                product = rec.product
                suggestions.append(
                    {
                        "label": label,
                        "name": product.name,
                        "price": f"${product.price:.2f}",
                        "description": product.description or "",
                        "image_url": product.image_url or product.thumbnail_url or "",
                    }
                )
            return suggestions[:3]
        except Exception as exc:
            logger.warning(
                "[REMINDER] Suggestion build failed for %s: %s", persona.name, exc
            )
            return []

    def build_email_html(
        self,
        persona: PersonaReminder,
        when_text: str,
        suggestions: List[dict],
    ) -> str:
        """Build HTML email content for birthday reminder"""
        last_gift_line = (
            f'<p style="margin: 0 0 12px; color: #555;">Last gift picked: {persona.last_gift}</p>'
            if persona.last_gift
            else ""
        )
        cards_html = ""
        for suggestion in suggestions:
            image_html = (
                f'<img src="{suggestion["image_url"]}" alt="{suggestion["name"]}" '
                'style="display: block; width: 100%; height: 140px; object-fit: cover;">'
                if suggestion["image_url"]
                else '<div style="height: 140px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 32px;">🎁</div>'
            )
            cards_html += f"""
        <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"border: 1px solid #e6e6e6; border-radius: 10px; overflow: hidden; margin-bottom: 16px;\">
            <tr>
                <td>{image_html}</td>
            </tr>
            <tr>
                <td style=\"padding: 16px;\">
                    <span style=\"display: inline-block; background: #d4403b; color: #ffffff; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;\">{suggestion["label"]}</span>
                    <h3 style=\"margin: 10px 0 4px; font-size: 16px; color: #333;\">{suggestion["name"]}</h3>
                    <p style=\"margin: 0 0 8px; color: #d4403b; font-weight: 700;\">{suggestion["price"]}</p>
                    <p style=\"margin: 0; color: #555; font-size: 13px; line-height: 1.4;\">{suggestion["description"]}</p>
                    <div style=\"margin-top: 12px;\">
                        <a href=\"#\" style=\"display: inline-block; padding: 8px 12px; background: #f5f5f5; color: #333; text-decoration: none; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px; font-weight: 600;\">View Product</a>
                    </div>
                </td>
            </tr>
        </table>
        """

        suggestions_block = (
            f"""
        <p style=\"margin: 0 0 12px; color: #555;\">Here are a few gift ideas:</p>
        {cards_html}
        """
            if suggestions
            else ""
        )

        return f"""
    <div style=\"background: #f6f6f6; padding: 24px; font-family: Arial, Helvetica, sans-serif;\">
        <div style=\"max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e6e6e6; border-radius: 12px; overflow: hidden;\">
            <div style=\"background: #d4403b; color: #ffffff; padding: 20px 24px;\">
                <h1 style=\"margin: 0; font-size: 20px;\">Gift Genius Reminder</h1>
                <p style=\"margin: 8px 0 0; font-size: 14px; opacity: 0.9;\">Birthday coming up {when_text}</p>
            </div>
            <div style=\"padding: 24px;\">
                <p style=\"margin: 0 0 12px; color: #333; font-size: 16px;\">Hi there,</p>
                <p style=\"margin: 0 0 12px; color: #555;\">Reminder: {persona.name}'s birthday is {when_text}.</p>
                {last_gift_line}
                {suggestions_block}
                <div style=\"margin-top: 20px;\">
                    <a href=\"#\" style=\"display: inline-block; padding: 10px 16px; background: #d4403b; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600;\">View More Gift Ideas</a>
                </div>
            </div>
            <div style=\"padding: 16px 24px; background: #fafafa; color: #888; font-size: 12px;\">
                You are receiving this reminder because email reminders are enabled in Gift Genius.
            </div>
        </div>
    </div>
    """

    def send_birthday_reminders(
        self,
        personas: List[PersonaReminder],
        user_email: Optional[str] = None,
    ) -> List[dict]:
        """Check for upcoming birthdays and send reminder emails"""
        today = datetime.now().date()
        sent = []

        for persona in personas:
            if not persona.email_reminders or not persona.birthday:
                continue

            try:
                birthday_date = datetime.strptime(persona.birthday, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(
                    "[REMINDER] Invalid birthday format for %s", persona.name
                )
                continue

            next_birthday = birthday_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)

            days_until = (next_birthday - today).days
            if days_until < 0 or days_until > 10:
                continue

            when_text = "today" if days_until == 0 else f"in {days_until} days"
            subject = f"Gift reminder: {persona.name}'s birthday is {when_text}"
            body_lines = [
                "Hi there,",
                "",
                f"Reminder: {persona.name}'s birthday is {when_text}.",
                "",
            ]
            if persona.last_gift:
                body_lines.append(f"Last gift picked: {persona.last_gift}")
                body_lines.append("")

            suggestions = self.format_suggestions(persona)
            if suggestions:
                body_lines.append("Here are a few gift ideas:")
                for suggestion in suggestions:
                    body_lines.append(
                        f"- {suggestion['label']}: {suggestion['name']} ({suggestion['price']})"
                    )
                body_lines.append("")

            body_lines.append("Open Gift Genius to see more gift suggestions.")
            body = "\n".join(body_lines)

            recipient = persona.user_email or user_email
            html_body = self.build_email_html(persona, when_text, suggestions)
            ok, status = self.send_email(subject, body, recipient, html_body)

            message = {
                "to": recipient or self.default_to,
                "subject": subject,
                "body": body,
                "body_html": html_body,
                "sent_at": datetime.now().isoformat(),
                "status": status,
            }
            self.email_inbox.append(message)
            if ok:
                sent.append({"name": persona.name, "status": status})

        return sent
