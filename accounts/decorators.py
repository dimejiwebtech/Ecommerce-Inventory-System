from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this area.')
            return redirect('accounts:login')
        if request.user.role not in ['staff', 'manager', 'admin']:
            messages.error(request, 'You do not have permission to access the IMS.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this area.')
            return redirect('accounts:login')
        if request.user.role not in ['manager', 'admin']:
            messages.error(request, 'You do not have permission to access this management feature.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this area.')
            return redirect('accounts:login')
        if request.user.role != 'admin':
            messages.error(request, 'Access restricted to administrators.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
