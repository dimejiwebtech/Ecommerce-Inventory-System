from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cart.models import Cart, CartItem, Wishlist, WishlistItem
from catalogue.models import Jewellery


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(user=None, session_key=session_key)
    return cart


def _cart_count_response(cart, request):
    if request.headers.get('HX-Request'):
        count = cart.item_count()
        return HttpResponse(
            f'<span id="cart-count" '
            f'class="absolute -top-2 -right-2 bg-shop-text text-white text-[10px] '
            f'font-bold h-4 w-4 rounded-full flex items-center justify-center '
            f'group-hover:bg-shop-gold transition-colors">{count}</span>'
        )
    return redirect('cart_detail')


def cart_detail(request):
    cart = get_or_create_cart(request)
    # The cart drawer requests ?partial=items to get just the items list
    if request.GET.get('partial') == 'items':
        return render(request, 'cart/partials/cart_items.html', {'cart': cart})
    # Summary-only refresh (called after HTMX updates)
    if request.GET.get('partial') == 'summary':
        return render(request, 'cart/partials/cart_summary.html', {'cart': cart})
    return render(request, 'cart/cart.html', {'cart': cart})


def cart_add(request):
    if request.method != 'POST':
        return redirect('shop_list')
    jewellery_id = request.POST.get('jewellery_id')
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')

    jewellery = get_object_or_404(Jewellery, id=jewellery_id, is_active=True)
    
    variant = None
    if variant_id:
        from catalogue.models import JewelleryVariant
        variant = get_object_or_404(JewelleryVariant, id=variant_id, jewellery=jewellery)
    
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, jewellery=jewellery, variant=variant)
    
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
        
    stock_limit = variant.stock if variant else jewellery.stock
    item.quantity = min(item.quantity, stock_limit)
    item.save()
    return _cart_count_response(cart, request)


def cart_add_pk(request, jewellery_id):
    jewellery = get_object_or_404(Jewellery, id=jewellery_id, is_active=True)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, jewellery=jewellery)
    if not created:
        item.quantity += 1
        item.quantity = min(item.quantity, jewellery.stock)
        item.save()
    return _cart_count_response(cart, request)


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    if request.headers.get('HX-Request'):
        cart.refresh_from_db()
        template_name = request.GET.get('template', 'cart/partials/cart_items.html')
        return render(request, template_name, {'cart': cart})
    return redirect('cart_detail')


def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            item.delete()
        else:
            item.quantity = min(qty, item.jewellery.stock)
            item.save()
    if request.headers.get('HX-Request'):
        cart.refresh_from_db()
        template_name = request.GET.get('template', 'cart/partials/cart_items.html')
        return render(request, template_name, {'cart': cart})
    return redirect('cart_detail')


def wishlist_toggle(request):
    if not request.user.is_authenticated:
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': f"{reverse('accounts:login')}?next={request.path}"})
        return redirect(f"{reverse('accounts:login')}?next={request.path}")

    if request.method != 'POST':
        return redirect('accounts:wishlist')
    jewellery_id = request.POST.get('jewellery_id')
    jewellery = get_object_or_404(Jewellery, id=jewellery_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    existing = WishlistItem.objects.filter(wishlist=wishlist, jewellery=jewellery).first()
    if existing:
        existing.delete()
        wished = False
    else:
        WishlistItem.objects.create(wishlist=wishlist, jewellery=jewellery)
        wished = True
    if request.headers.get('HX-Request'):
        return render(request, 'cart/partials/wishlist_toggle.html', {
            'jewellery': jewellery, 'wished': wished,
        })
    return redirect('product_detail', slug=jewellery.slug)


def wishlist_toggle_pk(request, jewellery_id):
    if not request.user.is_authenticated:
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': f"{reverse('accounts:login')}?next={request.path}"})
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    jewellery = get_object_or_404(Jewellery, id=jewellery_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    existing = WishlistItem.objects.filter(wishlist=wishlist, jewellery=jewellery).first()
    if existing:
        existing.delete()
        wished = False
    else:
        WishlistItem.objects.create(wishlist=wishlist, jewellery=jewellery)
        wished = True
    if request.headers.get('HX-Request'):
        return render(request, 'cart/partials/wishlist_toggle.html', {
            'jewellery': jewellery, 'wished': wished,
        })
    return redirect('product_detail', slug=jewellery.slug)


@login_required
def wishlist_page(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('jewellery__category')
    # attach display price
    for wi in items:
        p = wi.jewellery
        if (
            request.user.role == 'wholesaler'
            and hasattr(request.user, 'wholesaler_profile')
            and request.user.wholesaler_profile.is_verified
        ):
            wi.display_price = p.wholesale_price
        else:
            wi.display_price = p.retail_price
    return render(request, 'cart/wishlist.html', {'wishlist': wishlist, 'items': items})
