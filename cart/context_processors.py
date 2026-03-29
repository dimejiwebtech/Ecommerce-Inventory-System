from cart.models import Cart


def cart_context(request):
    """Inject cart item count into every template context."""
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(
                user=None, session_key=session_key
            ).first() if session_key else None

        if cart:
            count = cart.item_count()
    except Exception:
        pass

    return {'cart_count': count}
