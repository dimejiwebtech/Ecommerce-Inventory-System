from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order):
    """Sends a transactional email to the customer after order placement."""
    subject = f'Order Confirmation - #{order.order_number} | AURA Jewels'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [order.customer_email]
    
    html_content = render_to_string('emails/order_confirmation.html', {'order': order})
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
    except Exception as e:
        # Log error or handle gracefully
        print(f"Failed to send email: {e}")
