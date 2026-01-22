import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

class EmailService:
    """Basic SMTP email service"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@imagedescriber.com")

    async def send_email(self, to_email: str, subject: str, body: str, html: Optional[str] = None):
        """Send an email"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.smtp_from
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            # Add HTML part if provided
            if html:
                html_part = MIMEText(html, "html")
                message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            print(f"[Email] Sent email to {to_email}")
            return True
        except Exception as e:
            print(f"[Email] Failed to send email to {to_email}: {e}")
            return False

    async def sendWelcomeEmail(self, email: str, username: str):
        """Send welcome email after registration"""
        subject = "Welcome to Image Describer!"
        body = f"""
Hello {username},

Welcome to Image Describer! Your account has been successfully created.

You can now start using the application to generate descriptions for your images.

Best regards,
The Image Describer Team
        """

        html = f"""
<html>
<body>
    <h2>Welcome to Image Describer!</h2>
    <p>Hello <strong>{username}</strong>,</p>
    <p>Welcome to Image Describer! Your account has been successfully created.</p>
    <p>You can now start using the application to generate descriptions for your images.</p>
    <p>Best regards,<br>The Image Describer Team</p>
</body>
</html>
        """

        return await self.send_email(email, subject, body, html)

    async def sendPasswordResetEmail(self, email: str, username: str, reset_token: str):
        """Send password reset email"""
        subject = "Password Reset Request"
        body = f"""
Hello {username},

You requested a password reset for your Image Describer account.

Reset token: {reset_token}

If you didn't request this, please ignore this email.

Best regards,
The Image Describer Team
        """

        html = f"""
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Hello <strong>{username}</strong>,</p>
    <p>You requested a password reset for your Image Describer account.</p>
    <p><strong>Reset token:</strong> {reset_token}</p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Best regards,<br>The Image Describer Team</p>
</body>
</html>
        """

        return await self.send_email(email, subject, body, html)
