import csv
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render
from django.db.models import Sum, Count, F, Q, Avg, Value, CharField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import JsonResponse, HttpResponse

from orders.models import Order, OrderItem
from catalogue.models import Jewellery, Category
from accounts.models import CustomUser, WholesalerProfile
from accounts.decorators import staff_required
from pos.models import Sale, SaleItem


@staff_required
def ims_dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    revenue_statuses = ['processing', 'shipped', 'delivered']
    total_revenue = Order.objects.filter(
        status__in=revenue_statuses
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    monthly_revenue = Order.objects.filter(
        status__in=revenue_statuses,
        placed_at__date__gte=start_of_month
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    pending_wholesalers = WholesalerProfile.objects.filter(is_verified=False).count()

    low_stock_products = Jewellery.objects.filter(
        stock__lte=F('low_stock_threshold')
    ).order_by('stock')[:10]
    low_stock_count = Jewellery.objects.filter(
        stock__lte=F('low_stock_threshold')
    ).count()

    recent_orders = Order.objects.order_by('-placed_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'pending_wholesalers': pending_wholesalers,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'ims/dashboard.html', context)

@staff_required
def ims_sales_chart_data(request):
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    orders = Order.objects.filter(
        placed_at__date__gte=start_date,
        placed_at__date__lte=end_date,
        status__in=['processing', 'shipped', 'delivered']
    ).values('placed_at__date').annotate(
        revenue=Sum('grand_total')
    ).order_by('placed_at__date')

    labels = []
    data = []
    current_date = start_date
    orders_dict = {o['placed_at__date']: o['revenue'] for o in orders}

    while current_date <= end_date:
        labels.append(current_date.strftime("%b %d"))
        data.append(float(orders_dict.get(current_date, 0)))
        current_date += timedelta(days=1)

    return JsonResponse({'labels': labels, 'data': data})


@staff_required
def ims_notifications(request):
    new_orders_count = Order.objects.filter(status='pending').count()
    low_stock_count = Jewellery.objects.filter(
        stock__lte=F('low_stock_threshold')
    ).count()
    pending_wholesalers_count = WholesalerProfile.objects.filter(
        is_verified=False
    ).count()

    context = {
        'new_orders_count': new_orders_count,
        'low_stock_count': low_stock_count,
        'pending_wholesalers_count': pending_wholesalers_count,
    }
    return render(request, 'ims/partials/notifications.html', context)


def _parse_date_range(request):
    today = timezone.now().date()
    default_from = today.replace(day=1)
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    try:
        date_from = timezone.datetime.strptime(date_from_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = default_from

    try:
        date_to = timezone.datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_to = today

    return date_from, date_to


@staff_required
def ims_sales_report(request):
    date_from, date_to = _parse_date_range(request)
    valid_statuses = ['processing', 'shipped', 'delivered']

    # Online orders in date range
    online_orders = Order.objects.filter(
        placed_at__date__gte=date_from,
        placed_at__date__lte=date_to,
        status__in=valid_statuses,
    )
    online_revenue = online_orders.aggregate(
        total=Coalesce(Sum('grand_total'), Decimal('0'))
    )['total']
    online_count = online_orders.count()

    # POS sales in date range
    pos_sales_qs = Sale.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    )
    pos_revenue = pos_sales_qs.aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0'))
    )['total']
    pos_count = pos_sales_qs.count()

    # Totals
    total_revenue = online_revenue + pos_revenue
    total_transactions = online_count + pos_count
    avg_order_value = (total_revenue / total_transactions) if total_transactions else Decimal('0')

    # Top selling products (by quantity from OrderItem)
    top_products = OrderItem.objects.filter(
        order__placed_at__date__gte=date_from,
        order__placed_at__date__lte=date_to,
        order__status__in=valid_statuses,
    ).values(
        'jewellery_name', 'jewellery_sku'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum(F('unit_price') * F('quantity'))
    ).order_by('-units_sold')[:10]

    # Recent orders for the table
    recent_orders = online_orders.order_by('-placed_at')[:50]

    # CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{date_from}_{date_to}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order #', 'Customer', 'Status', 'Subtotal', 'Discount', 'Grand Total', 'Date'])
        for o in online_orders.order_by('-placed_at'):
            writer.writerow([
                o.order_number, o.customer_name, o.get_status_display(),
                o.subtotal, o.discount_amount, o.grand_total,
                o.placed_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'online_revenue': online_revenue,
        'pos_revenue': pos_revenue,
        'total_revenue': total_revenue,
        'online_count': online_count,
        'pos_count': pos_count,
        'total_transactions': total_transactions,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'ims/sales_report.html', context)


@staff_required
def ims_inventory_report(request):
    search_q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')  # all, low, out

    products = Jewellery.objects.select_related('category').annotate(
        retail_value=F('retail_price') * F('stock')
    )

    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) | Q(sku__icontains=search_q)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_filter == 'low':
        products = products.filter(stock__gt=0, stock__lte=F('low_stock_threshold'))
    elif stock_filter == 'out':
        products = products.filter(stock=0)

    # KPI summaries
    all_products = Jewellery.objects.all()
    total_skus = all_products.count()
    total_units = all_products.aggregate(total=Coalesce(Sum('stock'), 0))['total']
    total_retail_value = sum(p.retail_price * p.stock for p in all_products)
    total_wholesale_value = sum(p.wholesale_price * p.stock for p in all_products)
    low_stock_count = all_products.filter(stock__lte=F('low_stock_threshold'), stock__gt=0).count()
    out_of_stock_count = all_products.filter(stock=0).count()

    categories = Category.objects.all().order_by('name')

    # CSV Export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_valuation.csv"'
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Product Name', 'Category', 'Stock', 'Retail Price', 'Wholesale Price', 'Retail Value', 'Wholesale Value'])
        for p in products:
            writer.writerow([
                p.sku, p.name,
                p.category.name if p.category else '-',
                p.stock, p.retail_price, p.wholesale_price,
                p.retail_price * p.stock,
                p.wholesale_price * p.stock,
            ])
        return response

    context = {
        'products': products.order_by('name'),
        'total_skus': total_skus,
        'total_units': total_units,
        'total_retail_value': total_retail_value,
        'total_wholesale_value': total_wholesale_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'categories': categories,
        'search_q': search_q,
        'current_category': category_id,
        'current_stock': stock_filter,
    }
    return render(request, 'ims/inventory_report.html', context)


@staff_required
def ims_customer_report(request):
    date_from, date_to = _parse_date_range(request)
    role_filter = request.GET.get('role', '')  # customer, wholesaler, or empty=all
    search_q = request.GET.get('q', '').strip()

    users = CustomUser.objects.filter(
        role__in=['customer', 'wholesaler']
    ).annotate(
        order_count=Count(
            'orders',
            filter=Q(
                orders__placed_at__date__gte=date_from,
                orders__placed_at__date__lte=date_to,
                orders__status__in=['processing', 'shipped', 'delivered'],
            )
        ),
        total_spent=Coalesce(
            Sum(
                'orders__grand_total',
                filter=Q(
                    orders__placed_at__date__gte=date_from,
                    orders__placed_at__date__lte=date_to,
                    orders__status__in=['processing', 'shipped', 'delivered'],
                )
            ),
            Decimal('0')
        )
    ).order_by('-total_spent')

    if role_filter:
        users = users.filter(role=role_filter)
    if search_q:
        users = users.filter(
            Q(username__icontains=search_q) |
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(email__icontains=search_q)
        )

    # Summaries
    total_customers = CustomUser.objects.filter(role='customer').count()
    total_wholesalers = CustomUser.objects.filter(role='wholesaler').count()
    overall_revenue = users.aggregate(total=Coalesce(Sum('total_spent'), Decimal('0')))['total']

    # CSV Export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customer_report_{date_from}_{date_to}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Full Name', 'Email', 'Role', 'Orders', 'Total Spent'])
        for u in users:
            writer.writerow([
                u.username,
                f"{u.first_name} {u.last_name}".strip() or '-',
                u.email, u.get_role_display(),
                u.order_count, u.total_spent,
            ])
        return response

    context = {
        'users': users[:100],
        'date_from': date_from,
        'date_to': date_to,
        'total_customers': total_customers,
        'total_wholesalers': total_wholesalers,
        'overall_revenue': overall_revenue,
        'role_filter': role_filter,
        'search_q': search_q,
    }
    return render(request, 'ims/customer_report.html', context)
