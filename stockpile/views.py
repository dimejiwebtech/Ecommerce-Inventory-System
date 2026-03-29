from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Stockpile


@login_required
def stockpile_list(request):
    stockpiles = Stockpile.objects.filter(user=request.user, is_released=False)
    return render(request, 'stockpile/stockpile_list.html', {'stockpiles': stockpiles})


@login_required
def ims_stockpile_list(request):
    # Ensure only staff can access this
    if not request.user.role in ['staff', 'manager', 'admin']:
        return redirect('accounts:customer_dashboard')
        
    stockpiles = Stockpile.objects.filter(is_released=False).select_related('user', 'order_item__jewellery')
    total_unpaid_fees = sum(s.current_fee for s in stockpiles)
    
    return render(request, 'ims/stockpile_list.html', {
        'stockpiles': stockpiles,
        'total_unpaid_fees': total_unpaid_fees
    })
