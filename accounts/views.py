from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from cart.models import Cart, CartItem
from .forms import StaffUserForm
from django.urls import reverse
from accounts.decorators import staff_required
from accounts.emails import (
    send_otp_email,
    send_verification_email,
    send_welcome_email,
    send_wholesaler_pending_email,
    send_wholesaler_rejected_email,
)
from accounts.models import (
    CustomUser,
    EmailVerificationToken,
    LoginOTP,
    WholesalerContact,
    WholesalerProfile,
    otp_required_for,
)
from orders.models import Order
from cart.models import Wishlist
from .models import CustomerAddress, EmailVerificationToken
from .forms import AddressForm



def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        is_wholesaler = request.POST.get('is_wholesaler') == 'on'
        whatsapp = request.POST.get('whatsapp_number', '').strip()

        errors = {}

        if CustomUser.objects.filter(username=username).exists():
            errors['username'] = 'This username is already taken.'
        if CustomUser.objects.filter(email=email).exists():
            errors['email'] = 'An account with this email already exists.'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        if password != confirm:
            errors['confirm_password'] = 'Passwords do not match.'
        if is_wholesaler and not whatsapp:
            errors['whatsapp_number'] = 'Please enter your WhatsApp number.'

        wholesaler_status = None  # 'auto_approved' | 'pending' | 'rejected'
        if is_wholesaler and whatsapp and not errors:
            if WholesalerContact.number_exists(whatsapp):
                wholesaler_status = 'auto_approved'
            else:
                wholesaler_status = 'pending'

        if errors:
            return render(request, 'accounts/register.html', {
                'errors': errors,
                'post': request.POST,
            })

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='wholesaler' if is_wholesaler else 'customer',
        )

        if is_wholesaler:
            is_verified = wholesaler_status == 'auto_approved'
            WholesalerProfile.objects.create(
                user=user,
                whatsapp_number=whatsapp,
                is_verified=is_verified,
            )
            if wholesaler_status == 'auto_approved':
                pass  # welcome + verify email covers it
            else:
                send_wholesaler_pending_email(user)

        # Email verification token
        token = EmailVerificationToken.objects.create(user=user)
        send_verification_email(user, token)
        send_welcome_email(user)

        request.session['pending_verify_email'] = email
        return redirect('accounts:verify_email_sent')

    return render(request, 'accounts/register.html')


def verify_email_sent(request):
    email = request.session.get('pending_verify_email', '')
    return render(request, 'accounts/verify_email_sent.html', {'email': email})


def verify_email(request, token):
    obj = get_object_or_404(EmailVerificationToken, token=token)
    if obj.is_expired():
        return render(request, 'accounts/verify_email_expired.html', {'user': obj.user})
    user = obj.user
    user.is_email_verified = True
    user.save()
    obj.delete()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect(get_login_redirect_url(user))


def resend_verification(request):
    email = request.POST.get('email', '').strip()
    try:
        user = CustomUser.objects.get(email=email)
        if not user.is_email_verified:
            token, _ = EmailVerificationToken.objects.get_or_create(user=user)
            send_verification_email(user, token)
    except CustomUser.DoesNotExist:
        pass
    return render(request, 'accounts/verify_email_sent.html', {'email': email, 'resent': True})


def get_login_redirect_url(user):
    if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False) or getattr(user, 'role', '') in ['admin', 'manager', 'staff']:
        return reverse('reports:ims_dashboard')
    return reverse('accounts:customer_dashboard')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)

        if not user:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid email or password.',
                'post': request.POST,
            })

        if not user.is_email_verified:
            token, _ = EmailVerificationToken.objects.get_or_create(user=user)
            send_verification_email(user, token)
            return render(request, 'accounts/login.html', {
                'error': 'Please verify your email first. A new link has been sent.',
                'show_resend': True,
                'resend_email': user.email,
            })

        if otp_required_for(user):
            otp = LoginOTP.generate(user)
            send_otp_email(user, otp)
            request.session['otp_user_id'] = user.id
            return redirect('accounts:verify_otp')

        # Capture the anonymous session key BEFORE login() rotates it
        old_session_key = request.session.session_key
        login(request, user)
        _merge_session_cart(request, user, old_session_key)
        
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
            
        return redirect(get_login_redirect_url(user))

    return render(request, 'accounts/login.html')


def _merge_session_cart(request, user, old_session_key=None):
    """Transfer items from the anonymous session cart to the user's cart.
    
    Must be called with the session key captured BEFORE login() rotates it.
    """
    session_key = old_session_key or request.session.session_key
    if not session_key:
        return
    session_cart = Cart.objects.filter(user=None, session_key=session_key).first()
    if not session_cart:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)
    
    for item in session_cart.items.all():
        existing = CartItem.objects.filter(
            cart=user_cart, jewellery=item.jewellery, variant=item.variant
        ).first()
        if existing:
            existing.quantity += item.quantity
            stock = item.variant.stock if item.variant else item.jewellery.stock
            existing.quantity = min(existing.quantity, stock)
            existing.save()
        else:
            item.cart = user_cart
            item.save()
            
    session_cart.delete()


def verify_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        otp = LoginOTP.objects.filter(
            user=user, code=code, is_used=False
        ).first()

        if not otp or otp.is_expired():
            return render(request, 'accounts/verify_otp.html', {
                'error': 'Invalid or expired code. Please try again.',
                'user': user,
            })

        otp.is_used = True
        otp.save()
        del request.session['otp_user_id']
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(get_login_redirect_url(user))

    return render(request, 'accounts/verify_otp.html', {'user': user})


def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('accounts:login')
    user = get_object_or_404(CustomUser, id=user_id)
    otp = LoginOTP.generate(user)
    send_otp_email(user, otp)
    return render(request, 'accounts/verify_otp.html', {
        'user': user,
        'info': 'A new code has been sent to your email.',
    })

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()
    active_orders = Order.objects.filter(user=request.user, status__in=['pending', 'processing', 'shipped']).count()
    wishlist_obj = Wishlist.objects.filter(user=request.user).first()
    wishlist_items = wishlist_obj.items.select_related('jewellery').all()[:4] if wishlist_obj else []
    wishlist_count = wishlist_obj.items.count() if wishlist_obj else 0
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'orders': orders,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    })


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.save()
        p = user.profile
        p.address = request.POST.get('address', '')
        p.city = request.POST.get('city', '')
        p.state = request.POST.get('state', '')
        if request.FILES.get('avatar'):
            p.avatar = request.FILES['avatar']
        p.save()
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    address.delete()
    return redirect('accounts:address_list')


def resend_verification(request):
    email = request.session.get('pending_verify_email') or request.POST.get('email')
    if email:
        user = CustomUser.objects.filter(email=email).first()
        if user and not user.is_email_verified:
            token, _ = EmailVerificationToken.objects.get_or_create(user=user)
            send_verification_email(user, token)
            return render(request, 'accounts/verify_email_sent.html', {'email': email, 'info': 'Verification link resent!'})
    return redirect('accounts:login')


@staff_required
def ims_wholesaler_list(request):
    wholesalers = WholesalerProfile.objects.all().select_related('user').order_by('-applied_at')
    return render(request, 'ims/wholesaler_list.html', {'wholesalers': wholesalers})

@staff_required
def ims_wholesaler_detail(request, pk):
    profile = get_object_or_404(WholesalerProfile, pk=pk)
    return render(request, 'ims/wholesaler_detail.html', {'profile': profile})

@staff_required
def ims_wholesaler_approve(request, pk):
    profile = get_object_or_404(WholesalerProfile, pk=pk)
    profile.is_verified = True
    profile.verified_at = timezone.now()
    profile.save()
    messages.success(request, f"Wholesaler {profile.user.get_full_name()} has been approved.")
    return redirect('accounts_ims:ims_wholesaler_list')

@staff_required
def ims_wholesaler_reject(request, pk):
    profile = get_object_or_404(WholesalerProfile, pk=pk)
    # Optional: Deactivate the user or just keep as unverified
    profile.is_verified = False
    profile.save()
    messages.warning(request, f"Wholesaler {profile.user.get_full_name()} has been rejected.")
    return redirect('accounts_ims:ims_wholesaler_list')


@staff_required
def ims_staff_list(request):
    staff_users = CustomUser.objects.filter(role__in=['staff', 'manager', 'admin']).order_by('role')
    return render(request, 'ims/staff_list_management.html', {'staff_users': staff_users})

@staff_required
def ims_staff_add(request):
    if request.method == 'POST':
        form = StaffUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Staff member {user.username} created.")
            return redirect('accounts_ims:ims_staff_list')
    else:
        form = StaffUserForm()
    return render(request, 'ims/staff_form.html', {'form': form, 'title': 'Add Staff Member'})

@staff_required
def ims_staff_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = StaffUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Staff member {user.username} updated.")
            return redirect('accounts_ims:ims_staff_list')
    else:
        form = StaffUserForm(instance=user)
    return render(request, 'ims/staff_form.html', {'form': form, 'title': 'Edit Staff Member', 'staff_user': user})

@staff_required
def ims_staff_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('accounts_ims:ims_staff_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Staff member {username} deleted.")
        return redirect('accounts_ims:ims_staff_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': user, 'title': 'Delete Staff Member', 'back_url': 'accounts_ims:ims_staff_list'
    })
