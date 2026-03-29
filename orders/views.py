import json
from django_countries import countries as django_countries_list
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cart.models import Cart, CartItem
from cart.views import get_or_create_cart
from catalogue.models import Jewellery, StockMovement
from orders.models import Coupon, Order, OrderItem, OrderStatusHistory, ShippingAddress, Shipment
from django.contrib import messages
from accounts.decorators import staff_required
from .emails import send_order_confirmation_email

def get_countries():
    """Return countries list with Nigeria first, using django-countries."""
    result = [{"code": "NG", "name": "Nigeria"}]
    result += [
        {"code": code, "name": str(name)}
        for code, name in django_countries_list
        if code != "NG"
    ]
    return result


def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)
    error = None
    discount = 0

    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            error = 'This coupon is expired or no longer active.'
        elif cart.total() < coupon.min_order_value:
            error = f'Minimum order of ₦{coupon.min_order_value} required.'
        else:
            request.session['coupon_code'] = code
            if coupon.discount_type == 'percent':
                discount = (cart.total() * coupon.value) / 100
            else:
                discount = coupon.value
    except Coupon.DoesNotExist:
        error = 'Invalid coupon code.'

    return render(request, 'orders/partials/coupon_result.html', {
        'error': error,
        'discount': discount,
        'cart': cart,
    })


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        return redirect('cart_detail')

    coupon = None
    discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                if coupon.discount_type == 'percent':
                    discount = (cart.total() * coupon.value) / 100
                else:
                    discount = coupon.value
        except Coupon.DoesNotExist:
            pass

    if request.method == 'POST':
        # Build the order
        subtotal = cart.total()
        grand_total = max(subtotal - discount, 0)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        full_name = f"{first_name} {last_name}".strip() or request.user.get_full_name() or request.user.username

        order = Order.objects.create(
            user=request.user,
            customer_name=full_name,
            customer_email=request.POST.get('email', request.user.email),
            customer_phone=request.POST.get('phone', ''),
            subtotal=subtotal,
            discount_amount=discount,
            shipping_fee=0,
            grand_total=grand_total,
            coupon=coupon,
            notes=request.POST.get('notes', ''),
        )

        # Shipping address
        ShippingAddress.objects.create(
            order=order,
            full_name=full_name,
            address_line1=request.POST.get('address_line1', ''),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            postal_code=request.POST.get('postal_code', ''),
            country=request.POST.get('country', 'NG'),
            phone=request.POST.get('phone', ''),
        )

        # Create order items from cart + deduct stock
        for cart_item in cart.items.select_related('jewellery'):
            OrderItem.objects.create(
                order=order,
                jewellery=cart_item.jewellery,
                jewellery_name=cart_item.jewellery.name,
                jewellery_sku=cart_item.jewellery.sku,
                unit_price=cart_item.unit_price(),
                quantity=cart_item.quantity,
            )
            # Deduct stock
            j = cart_item.jewellery
            j.stock = max(j.stock - cart_item.quantity, 0)
            j.save()
            StockMovement.objects.create(
                jewellery=j,
                change=-cart_item.quantity,
                reason='sale',
                user=request.user,
            )

        # First status entry
        OrderStatusHistory.objects.create(order=order, status='pending')

        # Increment coupon usage
        if coupon:
            coupon.times_used += 1
            coupon.save()
            del request.session['coupon_code']

        # Clear cart
        cart.items.all().delete()

        # Send confirmation email
        send_order_confirmation_email(order)

        return redirect('accounts:order_confirm', ref_id=order.ref_id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'coupon': coupon,
        'discount': discount,
        'grand_total': max(cart.total() - discount, 0),
        'countries_list': get_countries(),
    })


def order_confirm(request, ref_id):
    order = get_object_or_404(Order, ref_id=ref_id)
    return render(request, 'orders/order_confirm.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, ref_id):
    order = get_object_or_404(Order, ref_id=ref_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@staff_required
def ims_order_list(request):
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort', '-placed_at')
    query = request.GET.get('q')
    
    orders = Order.objects.all().select_related('user')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if query:
        from django.db.models import Q
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_email__icontains=query)
        )
        
    orders = orders.order_by(sort_by)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'q': query,
        'status_choices': Order.STATUS_CHOICES
    }
    return render(request, 'ims/order_list.html', context)


@staff_required
def ims_order_detail(request, ref_id):
    order = get_object_or_404(Order, ref_id=ref_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.order_number} status updated to {new_status}.")
            return redirect('orders_ims:ims_order_detail', ref_id=order.ref_id)

    return render(request, 'ims/order_detail.html', {'order': order})


@staff_required
def ims_shipment_list(request):
    shipments = Shipment.objects.all().select_related('order').order_by('-created_at')
    return render(request, 'ims/shipment_list.html', {'shipments': shipments})


@staff_required
def ims_shipment_add(request, ref_id):
    order = get_object_or_404(Order, ref_id=ref_id)
    if hasattr(order, 'shipment'):
        return redirect('orders_ims:ims_shipment_edit', pk=order.shipment.pk)
        
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        carrier = request.POST.get('carrier')
        status = request.POST.get('status', 'preparing')
        notes = request.POST.get('notes', '')
        
        shipment = Shipment.objects.create(
            order=order,
            tracking_number=tracking_number,
            carrier=carrier,
            status=status,
            notes=notes
        )
        
        if status in ['shipped', 'in_transit']:
            order.status = 'shipped'
            order.save()
            OrderStatusHistory.objects.create(
                order=order, 
                status='shipped', 
                note=f"Shipment created: {carrier} {tracking_number}"
            )
            
        messages.success(request, f"Shipment created for Order {order.order_number}.")
        return redirect('orders_ims:ims_order_detail', ref_id=order.ref_id)
        
    return render(request, 'ims/shipment_form.html', {
        'order': order, 
        'status_choices': Shipment.SHIPMENT_STATUS
    })


@staff_required
def ims_shipment_edit(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    order = shipment.order
    
    if request.method == 'POST':
        shipment.tracking_number = request.POST.get('tracking_number')
        shipment.carrier = request.POST.get('carrier')
        old_status = shipment.status
        new_status = request.POST.get('status')
        shipment.status = new_status
        shipment.notes = request.POST.get('notes', '')
        shipment.save()
        
        if new_status != old_status:
            if new_status in ['shipped', 'in_transit']:
                order.status = 'shipped'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order, 
                    status='shipped', 
                    note=f"Shipment status updated to {new_status}"
                )
            elif new_status == 'delivered':
                order.status = 'delivered'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order, 
                    status='delivered', 
                    note="Shipment marked as delivered"
                )
        
        messages.success(request, f"Shipment for Order {order.order_number} updated.")
        return redirect('orders_ims:ims_order_detail', ref_id=order.ref_id)
        
    return render(request, 'ims/shipment_form.html', {
        'shipment': shipment, 
        'order': order, 
        'status_choices': Shipment.SHIPMENT_STATUS
    })
