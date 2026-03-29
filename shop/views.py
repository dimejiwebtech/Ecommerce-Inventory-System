from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from cart.models import Wishlist
from catalogue.models import Announcement, Category, Collection, Jewellery
from reviews.models import Review
from django.contrib import messages


def get_display_price(jewellery, user):
    if (
        user.is_authenticated
        and user.role == 'wholesaler'
        and hasattr(user, 'wholesaler_profile')
        and user.wholesaler_profile.is_verified
    ):
        return jewellery.wholesale_price
    return jewellery.retail_price


def home(request):
    featured = Jewellery.objects.filter(
        is_featured=True, is_active=True, stock__gt=0
    ).select_related('category', 'collection')[:8]

    best_sellers = Jewellery.objects.filter(
        is_active=True, stock__gt=0
    ).select_related('category')[:4]

    collections = Collection.objects.filter(is_featured=True, is_active=True)[:4]
    categories = Category.objects.filter(is_active=True)[:6]
    announcement = Announcement.objects.filter(is_active=True).first()

    # Attach display prices to featured products
    for p in featured:
        p.display_price = get_display_price(p, request.user)
    for p in best_sellers:
        p.display_price = get_display_price(p, request.user)

    return render(request, 'shop/home.html', {
        'featured': featured,
        'best_sellers': best_sellers,
        'collections': collections,
        'categories': categories,
        'announcement': announcement,
    })


def shop_list(request):
    products = Jewellery.objects.filter(is_active=True).select_related('category', 'collection')

    # Filters
    category_slug = request.GET.get('category')
    collection_slug = request.GET.get('collection')
    sort = request.GET.get('sort', 'name')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')

    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            products = products.filter(category=active_category)

    if collection_slug:
        products = products.filter(collection__slug=collection_slug)

    if min_price:
        products = products.filter(retail_price__gte=min_price)
    if max_price:
        products = products.filter(retail_price__lte=max_price)
    if in_stock:
        products = products.filter(stock__gt=0)

    sort_map = {
        'name': 'name',
        'price_asc': 'retail_price',
        'price_desc': '-retail_price',
        'newest': '-created_at',
        'bestselling': '-stock',
    }
    products = products.order_by(sort_map.get(sort, 'name'))

    # Attach display price
    for p in products:
        p.display_price = get_display_price(p, request.user)

    categories = Category.objects.filter(is_active=True)
    collections = Collection.objects.filter(is_active=True)

    ctx = {
        'products': products,
        'categories': categories,
        'collections': collections,
        'active_category': active_category,
        'current_sort': sort,
        'current_filters': request.GET,
    }

    # HTMX partial response
    if request.headers.get('HX-Request'):
        return render(request, 'shop/partials/product_grid.html', ctx)
    return render(request, 'shop/shop.html', ctx)


def product_detail(request, slug):
    product = get_object_or_404(Jewellery, slug=slug, is_active=True)
    
    # Review submission
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={'rating': rating, 'comment': comment, 'is_approved': False}
            )
            messages.success(request, "Your review has been submitted and is pending approval.")
            return redirect('product_detail', slug=product.slug)

    images = product.images.all()
    variants = product.variants.all()
    reviews = product.reviews.filter(is_approved=True)
    
    related = Jewellery.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    # Wishlist state
    wished = False
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wished = wishlist.items.filter(jewellery=product).exists()

    display_price = get_display_price(product, request.user)
    for r in related:
        r.display_price = get_display_price(r, request.user)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'images': images,
        'variants': variants,
        'reviews': reviews,
        'related': related,
        'display_price': display_price,
        'wished': wished,
    })


def collections(request):
    all_collections = Collection.objects.filter(is_active=True)
    return render(request, 'shop/collections.html', {'collections': all_collections})


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug, is_active=True)
    products = Jewellery.objects.filter(
        collection=collection, is_active=True
    ).select_related('category')
    for p in products:
        p.display_price = get_display_price(p, request.user)
    return render(request, 'shop/collection_detail.html', {
        'collection': collection,
        'products': products,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = Jewellery.objects.filter(
            is_active=True
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(sku__icontains=query) |
            models.Q(category__name__icontains=query)
        ).select_related('category')[:20]
        for r in results:
            r.display_price = get_display_price(r, request.user)

    if request.headers.get('HX-Request'):
        return render(request, 'shop/partials/search_results.html', {
            'results': results, 'query': query
        })
    return render(request, 'shop/search.html', {
        'results': results, 'query': query
    })


def newsletter_signup(request):
    if request.method == 'POST':
        # Placeholder — wire to MailerLite/SendGrid later
        if request.headers.get('HX-Request'):
            return render(request, 'shop/partials/newsletter_success.html')
    return redirect('home')


def announcement_banner(request):
    announcement = Announcement.objects.filter(is_active=True).first()
    return render(request, 'shop/partials/announcement_banner.html', {
        'announcement': announcement
    })
