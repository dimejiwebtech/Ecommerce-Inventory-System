from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from accounts.decorators import staff_required
from .models import Bill

@staff_required
def ims_bill_list(request):
    bills = Bill.objects.all()
    
    # Optional search filtering
    q = request.GET.get('q', '')
    if q:
        bills = bills.filter(institution_name__icontains=q) | bills.filter(description__icontains=q)
        
    return render(request, 'ims/bill_list.html', {
        'bills': bills,
        'q': q
    })

@staff_required
def ims_bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'ims/bill_detail.html', {'bill': bill})

@staff_required
def ims_bill_add(request):
    if request.method == 'POST':
        try:
            bill = Bill.objects.create(
                institution_name=request.POST.get('institution_name'),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                description=request.POST.get('description', ''),
                payment_details=request.POST.get('payment_details', ''),
                amount=request.POST.get('amount'),
                status=request.POST.get('status', 'unpaid'),
                due_date=request.POST.get('due_date') or None
            )
            messages.success(request, f"Bill for {bill.institution_name} added successfully.")
            return redirect('bills:ims_bill_list')
        except Exception as e:
            messages.error(request, f"Error adding bill: {e}")
            
    return render(request, 'ims/bill_form.html', {'is_edit': False})

@staff_required
def ims_bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    
    if request.method == 'POST':
        try:
            bill.institution_name = request.POST.get('institution_name')
            bill.phone = request.POST.get('phone', '')
            bill.email = request.POST.get('email', '')
            bill.address = request.POST.get('address', '')
            bill.description = request.POST.get('description', '')
            bill.payment_details = request.POST.get('payment_details', '')
            bill.amount = request.POST.get('amount')
            bill.status = request.POST.get('status', 'unpaid')
            
            due_date = request.POST.get('due_date')
            bill.due_date = due_date if due_date else None
            
            bill.save()
            messages.success(request, f"Bill for {bill.institution_name} updated successfully.")
            return redirect('bills:ims_bill_list')
        except Exception as e:
            messages.error(request, f"Error updating bill: {e}")
            
    return render(request, 'ims/bill_form.html', {'is_edit': True, 'bill': bill})

@staff_required
def ims_bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        name = bill.institution_name
        bill.delete()
        messages.success(request, f"Bill {name} has been deleted.")
        return redirect('bills:ims_bill_list')
    return render(request, 'ims/confirm_delete.html', {
        'title': 'Delete Bill',
        'message': f"Are you sure you want to delete the bill for {bill.institution_name} (₦{bill.amount})?",
        'cancel_url': reverse('bills:ims_bill_list') if 'django.urls.reverse' not in str(type(Exception)) else f"/ims/bills/"
    })
