from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


SITE_URL = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


def _send(subject, template, context, to_email):
    html = render_to_string(template, context)
    send_mail(
        subject=subject,
        message=strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=html,
        fail_silently=False,
    )


def send_verification_email(user, token):
    verify_url = f"{SITE_URL}/accounts/verify-email/{token.token}/"
    _send(
        subject='Verify your AURA account',
        template='emails/verify_email.html',
        context={'user': user, 'verify_url': verify_url},
        to_email=user.email,
    )


def send_welcome_email(user):
    _send(
        subject='Welcome to AURA Jewellery!',
        template='emails/welcome_customer.html',
        context={'user': user, 'site_url': SITE_URL},
        to_email=user.email,
    )


def send_otp_email(user, otp):
    _send(
        subject=f'Your AURA login code: {otp.code}',
        template='emails/login_otp.html',
        context={'user': user, 'code': otp.code},
        to_email=user.email,
    )


def send_wholesaler_pending_email(user):
    _send(
        subject='Wholesaler Application Received — AURA',
        template='emails/wholesaler_pending.html',
        context={'user': user, 'site_url': SITE_URL},
        to_email=user.email,
    )


def send_wholesaler_approved_email(user):
    _send(
        subject='Your Wholesale Account is Approved! — AURA',
        template='emails/wholesaler_approved.html',
        context={'user': user, 'site_url': SITE_URL},
        to_email=user.email,
    )


def send_wholesaler_rejected_email(user):
    _send(
        subject='Wholesaler Application Update — AURA',
        template='emails/wholesaler_rejected.html',
        context={'user': user, 'site_url': SITE_URL},
        to_email=user.email,
    )


def send_order_confirmation_email(order):
    _send(
        subject=f'Order Confirmed: {order.order_number}',
        template='emails/order_confirmation.html',
        context={'order': order, 'site_url': SITE_URL},
        to_email=order.customer_email,
    )
