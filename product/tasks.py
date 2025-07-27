from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation_email(email, order_id):
    subject = f"Your Order #{order_id} has been placed!"
    message = f"Thank you for your order #{order_id}.\nWe are processing it and will notify you soon."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return {"success":True}