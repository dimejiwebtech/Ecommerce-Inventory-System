from orders.models import Order

def orders_context(request):
    """Context processor for order-related data in the IMS."""
    if not request.user.is_authenticated or not request.user.role in ['staff', 'manager', 'admin']:
        return {}
        
    return {
        'online_order_count': Order.objects.filter(status='pending').count()
    }
