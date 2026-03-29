from django import forms
from .models import CustomerAddress, CustomUser

class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-shop-border px-4 py-3 text-sm focus:outline-none focus:border-shop-gold bg-white'
            })

    class Meta:
        model = CustomerAddress
        fields = [
            'full_name', 'phone', 'email', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'postal_code', 'is_default'
        ]
        widgets = {
            'is_default': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-shop-gold border-shop-border rounded focus:ring-shop-gold'}),
        }

class StaffUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'
                })

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']
        widgets = {
            'role': forms.Select(),
            'is_active': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
        }
