from django.core.mail import send_mail
from django.conf import settings
from typing import List

def send_email(to_addresses: List[str], message: str) -> None:
    """
    Send email notification using Django's email system
    """
    send_mail(
        subject="Sanparks Availability Alert",
        message="",  # Empty plain text message
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=to_addresses,
        html_message=message,
        fail_silently=False,
    )
