from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction, models
from django.contrib import messages
from accounts.decorators import staff_required
from catalogue.models import Jewellery, JewelleryVariant, StockMovement
from .models import Sale, SaleItem
import json

@staff_required
def ims_pos(request):
    return render(request, 'ims/pos_interface.html')

@staff_required
def ims_pos_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if len(query) >= 2:
        # Search base products
        products = Jewellery.objects.filter(
            models.Q(name__icontains=query) | models.Q(sku__icontains=query)
        ).select_related('category')[:10]
        
        for p in products:
            # If product has variants, we show variants. If not, we show base.
            variants = p.variants.all()
            if variants.exists():
                for v in variants:
                    results.append({
                        'id': p.id,
                        'variant_id': v.id,
                        'name': f"{p.name} ({v.color or ''} {v.size or ''})",
                        'sku': p.sku,
                        'price': float(p.retail_price),
                        'stock': v.stock,
                        'category': p.category.name if p.category else 'N/A'
                    })
            else:
                results.append({
                    'id': p.id,
                    'variant_id': None,
                    'name': p.name,
                    'sku': p.sku,
                    'price': float(p.retail_price),
                    'stock': p.stock,
                    'category': p.category.name if p.category else 'N/A'
                })
    
    return JsonResponse({'results': results})

@staff_required
@require_POST
def ims_pos_checkout(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        total_amount = data.get('total', 0)
        customer_name = data.get('customer_name', '')
        customer_phone = data.get('customer_phone', '')

        if not items:
            return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)

        with transaction.atomic():
            # Create Sale record
            sale = Sale.objects.create(
                staff=request.user,
                total_amount=total_amount,
                payment_method=payment_method,
                customer_name=customer_name,
                customer_phone=customer_phone
            )

            for item in items:
                p_id = item.get('id')
                v_id = item.get('variant_id')
                qty = int(item.get('quantity', 1))
                price = item.get('price')

                product = Jewellery.objects.select_for_update().get(id=p_id)
                variant = None
                
                if v_id:
                    variant = JewelleryVariant.objects.select_for_update().get(id=v_id)
                    if variant.stock < qty:
                        raise ValueError(f"Insufficient stock for {variant}")
                    variant.stock -= qty
                    variant.save()
                else:
                    if product.stock < qty:
                        raise ValueError(f"Insufficient stock for {product.name}")
                    product.stock -= qty
                    product.save()

                # Create SaleItem
                SaleItem.objects.create(
                    sale=sale,
                    jewellery=product,
                    variant=variant,
                    quantity=qty,
                    unit_price=price,
                    subtotal=float(price) * qty
                )

                # Log Stock Movement
                StockMovement.objects.create(
                    jewellery=product,
                    user=request.user,
                    change=-qty,
                    reason=f"POS Sale #{sale.id}",
                    note=f"In-store sale via POS"
                )

        return JsonResponse({
            'success': True, 
            'sale_id': sale.id,
            'message': 'Sale completed successfully!'
        })

    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred during checkout'}, status=500)
