from django import forms
from django.forms import inlineformset_factory, ModelForm
from .models import Jewellery, Category, Collection, JewelleryImage, Vendor, PurchaseOrder, PurchaseOrderItem, JewelleryVariant, Announcement
from tinymce.widgets import TinyMCE

class JewelleryVariantForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'
            })

    class Meta:
        model = JewelleryVariant
        fields = ['size', 'color', 'stock', 'image']


class JewelleryImageForm(forms.ModelForm):
    class Meta:
        model = JewelleryImage
        fields = ['image', 'alt_text', 'is_primary', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 cursor-pointer'}),
            'alt_text': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'placeholder': 'Optional label'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)] cursor-pointer'}),
            'order': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
        }

JewelleryImageFormSet = inlineformset_factory(
    Jewellery, JewelleryImage, form=JewelleryImageForm,
    extra=1, can_delete=True
)

JewelleryVariantFormSet = inlineformset_factory(
    Jewellery, JewelleryVariant, form=JewelleryVariantForm,
    extra=1, can_delete=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
        }

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'banner', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'rows': 4}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
        }

class JewelleryForm(forms.ModelForm):
    class Meta:
        model = Jewellery
        fields = [
            'name', 'sku', 'description', 'category', 'collection',
            'retail_price', 'wholesale_price', 'stock', 'low_stock_threshold',
            'weight_grams', 'is_featured', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'sku': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'description': TinyMCE(attrs={'cols': 80, 'rows': 15}),
            'category': forms.Select(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'}),
            'collection': forms.Select(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'}),
            'retail_price': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'wholesale_price': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'weight_grams': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['text', 'link', 'link_label', 'is_active']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'link': forms.URLInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'link_label': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'accent-[var(--ims-accent)]'}),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'address': forms.Textarea(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'rows': 3}),
        }

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'vendor', 'status', 'order_date', 'notes']
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm'}),
            'vendor': forms.Select(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'}),
            'status': forms.Select(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm bg-white'}),
            'order_date': forms.DateInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:border-[var(--ims-accent)] text-sm', 'rows': 3}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['jewellery', 'quantity', 'unit_cost']
        widgets = {
            'jewellery': forms.Select(attrs={'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--ims-accent)] text-xs bg-white'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--ims-accent)] text-xs'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--ims-accent)] text-xs'}),
        }

PurchaseOrderItemFormSet = forms.inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemForm, extra=2, can_delete=True
)
