import io

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages as msg

from accounts.models import (
    Customer,
    CustomUser,
    EmailVerificationToken,
    LoginOTP,
    Profile,
    Vendor,
    WholesalerContact,
    WholesalerProfile,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'is_email_verified')}),
    )


@admin.register(WholesalerProfile)
class WholesalerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'whatsapp_number', 'is_verified', 'applied_at')
    list_filter = ('is_verified',)
    actions = ['approve_wholesalers', 'reject_wholesalers']

    def approve_wholesalers(self, request, queryset):
        queryset.update(is_verified=True, verified_at=timezone.now())
        for profile in queryset:
            from accounts.emails import send_wholesaler_approved_email
            send_wholesaler_approved_email(profile.user)
    approve_wholesalers.short_description = 'Approve selected wholesalers'

    def reject_wholesalers(self, request, queryset):
        queryset.update(is_verified=False)
        for profile in queryset:
            from accounts.emails import send_wholesaler_rejected_email
            send_wholesaler_rejected_email(profile.user)
    reject_wholesalers.short_description = 'Reject selected wholesalers'


@admin.register(WholesalerContact)
class WholesalerContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'raw_number', 'normalised', 'uploaded_at')
    search_fields = ('name', 'normalised')
    actions = ['upload_contacts_from_csv']

    def upload_contacts_from_csv(self, request, queryset):
        self.message_user(request, 'Use the Upload Contacts page to import from CSV/Excel.')
    upload_contacts_from_csv.short_description = 'Import contacts from CSV/Excel'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [path('upload-csv/', self.admin_site.admin_view(self.upload_csv_view), name='upload_contacts_csv')]
        return custom + urls

    def upload_csv_view(self, request):

        if request.method == 'POST' and request.FILES.get('csv_file'):
            f = request.FILES['csv_file']
            name_col = int(request.POST.get('name_col', 0))
            number_col = int(request.POST.get('number_col', 1))
            skip_header = request.POST.get('skip_header') == 'on'

            created = 0
            skipped = 0

            if f.name.endswith(('.xlsx', '.xls')):
                import openpyxl
                wb = openpyxl.load_workbook(f)
                rows = list(wb.active.iter_rows(values_only=True))
            else:
                import csv
                content = f.read().decode('utf-8-sig')
                rows = list(csv.reader(io.StringIO(content)))

            for i, row in enumerate(rows):
                if skip_header and i == 0:
                    continue
                try:
                    name = str(row[name_col]).strip() if len(row) > name_col else ''
                    number = str(row[number_col]).strip() if len(row) > number_col else ''
                    if not number:
                        continue
                    _, c = WholesalerContact.objects.get_or_create(
                        raw_number=number,
                        defaults={'name': name}
                    )
                    if c:
                        created += 1
                    else:
                        skipped += 1
                except Exception:
                    skipped += 1

            msg.success(request, f'{created} contacts imported, {skipped} skipped/duplicates.')
            return redirect('..')

        return render(request, 'ims/admin/upload_contacts.html')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'status')
    list_filter = ('status',)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'email')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'loyalty_points', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('token', 'created_at')


@admin.register(LoginOTP)
class LoginOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_used', 'created_at')
    list_filter = ('is_used',)
    readonly_fields = ('code', 'created_at')

