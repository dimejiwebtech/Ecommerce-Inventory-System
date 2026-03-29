from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import staff_required
from .models import Review

@staff_required
def ims_review_list(request):
    reviews = Review.objects.all().select_related('product', 'user')
    status_filter = request.GET.get('status')
    
    if status_filter == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif status_filter == 'pending':
        reviews = reviews.filter(is_approved=False)
        
    return render(request, 'ims/review_list.html', {
        'reviews': reviews,
        'status_filter': status_filter
    })

@staff_required
def ims_review_approve(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, f"Review by {review.user.username} approved.")
    return redirect('reviews:ims_review_list')

@staff_required
def ims_review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    username = review.user.username
    review.delete()
    messages.success(request, f"Review by {username} deleted.")
    return redirect('reviews:ims_review_list')
