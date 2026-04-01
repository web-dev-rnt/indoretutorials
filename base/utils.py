# utils.py
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.conf import settings
import logging
import socket
import threading

logger = logging.getLogger(__name__)


def get_active_smtp_config():
    """Get active SMTP config that passed test_status='success'."""
    try:
        from adminpanel.models import SMTPConfiguration
        return SMTPConfiguration.objects.filter(
            is_active=True,
            test_status='success',
        ).first()
    except Exception as e:
        logger.error(f"Error getting SMTP configuration: {e}")
        return None


def has_smtp_configured():
    """Check if SMTP is ready to use."""
    return get_active_smtp_config() is not None


# ✅ REMOVED: configure_smtp_settings() and restore_smtp_settings()
# They were mutating global settings — NOT thread-safe.


def send_otp_email(user, otp_code, timeout=15):
    """
    Send OTP email using a direct per-call SMTP connection.
    Does NOT touch global Django settings — fully thread-safe.
    """
    smtp_config = get_active_smtp_config()
    if not smtp_config:
        return False, "No working SMTP configuration found."

    try:
        subject = "Email Verification - OTP Code"
        context = {"user": user, "otp_code": otp_code, "site_name": "Your Site"}

        try:
            html_message = render_to_string("emails/otp_verification.html", context)
        except Exception:
            html_message = None

        plain_message = f"""
Hello {user.first_name or user.email},
Your OTP is: {otp_code}
This OTP expires in 10 minutes.
Thanks,
Your Site Team
        """

        # ✅ Build a dedicated connection using smtp_config values directly
        # This never touches global settings — safe to use in any thread
        connection = get_connection(
            backend=smtp_config.email_backend,
            host=smtp_config.email_host,
            port=smtp_config.email_port,
            username=smtp_config.email_host_user,
            password=smtp_config.email_host_password,
            use_tls=smtp_config.email_use_tls,
            use_ssl=smtp_config.email_use_ssl,
            timeout=timeout,  # ✅ Timeout set here — no socket.setdefaulttimeout needed
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=smtp_config.default_from_email,
            to=[user.email],
            connection=connection,
        )

        if html_message:
            email.attach_alternative(html_message, "text/html")

        email.send(fail_silently=False)

        return True, "OTP sent successfully"

    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
        return False, f"Email failed: {str(e)}"
    # ✅ REMOVED: finally block with restore_smtp_settings — no longer needed


class _OTPEmailThread(threading.Thread):
    """Daemon thread to send OTP email without blocking the signup response."""

    def __init__(self, user, otp, timeout=15):
        super().__init__(daemon=True)
        self.user = user
        self.otp = otp
        self.timeout = timeout

    def run(self):
        try:
            success, message = send_otp_email(self.user, self.otp.otp_code, timeout=self.timeout)
            if not success:
                logger.warning(
                    f"Background OTP email failed for {self.user.email}: {message}. "
                    f"OTP ID={self.otp.pk} marked as used."
                )
                self.otp.is_used = True
                self.otp.save(update_fields=['is_used'])
        except Exception as e:
            logger.error(f"OTPEmailThread crashed for {self.user.email}: {e}")


def create_and_send_otp(user, verification_type="email", is_mobile=False):
    """
    Create OTP instantly + fire email in a background thread.
    Signup response is NOT blocked by email sending.
    """
    from base.models import OTPVerification

    # Deactivate previous OTPs
    OTPVerification.objects.filter(
        user=user,
        verification_type=verification_type,
    ).update(is_used=True)

    # Create new OTP — instant DB write
    otp = OTPVerification.objects.create(
        user=user,
        verification_type=verification_type,
    )

    smtp_config = get_active_smtp_config()
    if not smtp_config:
        return otp, "No SMTP - direct login"

    # Fire email in background — response is not blocked
    _OTPEmailThread(user, otp, timeout=15).start()

    return otp, "OTP sending in background"
