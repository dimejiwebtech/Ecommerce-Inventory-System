from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Jewellery, Category, Collection, Vendor, PurchaseOrder, PurchaseOrderItem, StockMovement, Announcement
from .forms import JewelleryForm, CategoryForm, CollectionForm, VendorForm, PurchaseOrderForm, PurchaseOrderItemFormSet, AnnouncementForm, JewelleryImageFormSet, JewelleryVariantFormSet
from accounts.decorators import staff_required
from .forms import JewelleryVariantForm
from .models import JewelleryVariant
@staff_required
def ims_product_list(request):
    products = Jewellery.objects.all().select_related('category', 'collection').order_by('-created_at')
    return render(request, 'ims/product_list.html', {'products': products})

@staff_required
def ims_product_add(request):
    if request.method == 'POST':
        form = JewelleryForm(request.POST, request.FILES)
        image_formset = JewelleryImageFormSet(request.POST, request.FILES)
        variant_formset = JewelleryVariantFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid() and variant_formset.is_valid():
            product = form.save()
            image_formset.instance = product
            image_formset.save()
            variant_formset.instance = product
            variant_formset.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('catalogue:ims_product_list')
    else:
        form = JewelleryForm()
        image_formset = JewelleryImageFormSet()
        variant_formset = JewelleryVariantFormSet()
    return render(request, 'ims/product_form.html', {
        'form': form, 
        'image_formset': image_formset, 
        'variant_formset': variant_formset, 
        'title': 'Add Product'
    })

@staff_required
def ims_product_edit(request, pk):
    product = get_object_or_404(Jewellery, pk=pk)
    if request.method == 'POST':
        form = JewelleryForm(request.POST, request.FILES, instance=product)
        image_formset = JewelleryImageFormSet(request.POST, request.FILES, instance=product)
        variant_formset = JewelleryVariantFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and image_formset.is_valid() and variant_formset.is_valid():
            form.save()
            image_formset.save()
            variant_formset.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('catalogue:ims_product_list')
    else:
        form = JewelleryForm(instance=product)
        image_formset = JewelleryImageFormSet(instance=product)
        variant_formset = JewelleryVariantFormSet(instance=product)
    return render(request, 'ims/product_form.html', {
        'form': form, 
        'image_formset': image_formset, 
        'variant_formset': variant_formset, 
        'title': 'Edit Product', 
        'product': product
    })

@staff_required
def ims_product_delete(request, pk):
    product = get_object_or_404(Jewellery, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('catalogue:ims_product_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': product, 'title': 'Delete Product', 'back_url': 'catalogue:ims_product_list'
    })


@staff_required
def ims_category_list(request):
    categories = Category.objects.all()
    return render(request, 'ims/category_list.html', {'categories': categories})

@staff_required
def ims_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Category "{cat.name}" created.')
            return redirect('catalogue:ims_category_list')
    else:
        form = CategoryForm()
    return render(request, 'ims/category_form.html', {'form': form, 'title': 'Add Category'})

@staff_required
def ims_category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{cat.name}" updated.')
            return redirect('catalogue:ims_category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'ims/category_form.html', {'form': form, 'title': 'Edit Category', 'category': cat})


@staff_required
def ims_collection_list(request):
    collections = Collection.objects.all()
    return render(request, 'ims/collection_list.html', {'collections': collections})

@staff_required
def ims_collection_add(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            col = form.save()
            messages.success(request, f'Collection "{col.name}" created.')
            return redirect('catalogue:ims_collection_list')
    else:
        form = CollectionForm()
    return render(request, 'ims/collection_form.html', {'form': form, 'title': 'Add Collection'})

@staff_required
def ims_announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'ims/announcement_list.html', {'announcements': announcements})

@staff_required
def ims_announcement_add(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('catalogue:ims_announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'ims/announcement_form.html', {'form': form, 'title': 'Add Announcement'})

@staff_required
def ims_announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully.')
            return redirect('catalogue:ims_announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'ims/announcement_form.html', {'form': form, 'title': 'Edit Announcement', 'announcement': announcement})

@staff_required
def ims_announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
        return redirect('catalogue:ims_announcement_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': announcement, 'title': 'Delete Announcement', 'back_url': 'catalogue:ims_announcement_list'
    })

@staff_required
def ims_collection_edit(request, pk):
    col = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=col)
        if form.is_valid():
            form.save()
            messages.success(request, f'Collection "{col.name}" updated.')
            return redirect('catalogue:ims_collection_list')
    else:
        form = CollectionForm(instance=col)
    return render(request, 'ims/collection_form.html', {'form': form, 'title': 'Edit Collection', 'collection': col})
    return render(request, 'ims/collection_form.html', {'form': form, 'title': 'Edit Collection', 'collection': col})


@staff_required
def ims_vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'ims/vendor_list.html', {'vendors': vendors})

@staff_required
def ims_vendor_add(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" added.')
            return redirect('catalogue:ims_vendor_list')
    else:
        form = VendorForm()
    return render(request, 'ims/vendor_form.html', {'form': form, 'title': 'Add Vendor'})

@staff_required
def ims_vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vendor "{vendor.name}" updated.')
            return redirect('catalogue:ims_vendor_list')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'ims/vendor_form.html', {'form': form, 'title': 'Edit Vendor', 'vendor': vendor})


@staff_required
def ims_po_list(request):
    pos = PurchaseOrder.objects.all().select_related('vendor').order_by('-created_at')
    return render(request, 'ims/po_list.html', {'pos': pos})

@staff_required
def ims_po_add(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save()
            messages.success(request, f'Purchase Order {po.po_number} created.')
            return redirect('catalogue:ims_po_edit', pk=po.pk)
    else:
        form = PurchaseOrderForm(initial={'po_number': f'PO-{timezone.now().strftime("%y%m%d%H%M")}'})
    return render(request, 'ims/po_form.html', {'form': form, 'title': 'Create PO'})

@staff_required
def ims_po_edit(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=po)
        formset = PurchaseOrderItemFormSet(request.POST, instance=po)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            # Update PO total
            po.update_total()
            messages.success(request, f'PO {po.po_number} updated.')
            return redirect('catalogue:ims_po_list')
    else:
        form = PurchaseOrderForm(instance=po)
        formset = PurchaseOrderItemFormSet(instance=po)
    
    return render(request, 'ims/po_form.html', {
        'form': form, 
        'formset': formset,
        'title': f'Edit {po.po_number}', 
        'po': po
    })

@staff_required
def ims_po_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status == 'received':
        messages.warning(request, "This PO has already been received.")
        return redirect('catalogue:ims_po_list')
        
    if request.method == 'POST':
        with transaction.atomic():
            po.status = 'received'
            po.received_date = timezone.now().date()
            po.save()
            
            # Update stock for each item
            for item in po.items.all():
                product = item.jewellery
                product.stock += item.quantity
                product.save()
                
                # Log movement
                StockMovement.objects.create(
                    jewellery=product,
                    change=item.quantity,
                    reason='purchase',
                    note=f'Received via {po.po_number}',
                    user=request.user
                )
                
            messages.success(request, f'Purchase Order {po.po_number} received. Inventory updated.')
        return redirect('catalogue:ims_po_list')
        
@staff_required
def ims_stock_movements(request):
    movements = StockMovement.objects.all().select_related('jewellery', 'user').order_by('-created_at')
    return render(request, 'ims/stock_movements.html', {'movements': movements})


# Variations & Sizes
@staff_required
def ims_variant_list(request):
    variants = JewelleryVariant.objects.all().select_related('jewellery').order_by('jewellery__name')
    return render(request, 'ims/variant_list.html', {'variants': variants})

@staff_required
def ims_variant_add(request):
    if request.method == 'POST':
        form = JewelleryVariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save()
            messages.success(request, f"Variant for {variant.jewellery.name} created.")
            return redirect('catalogue:ims_variant_list')
    else:
        product_id = request.GET.get('product')
        initial = {'jewellery': product_id} if product_id else {}
        form = JewelleryVariantForm(initial=initial)
    return render(request, 'ims/variant_form.html', {'form': form, 'title': 'Add Variation'})

@staff_required
def ims_variant_edit(request, pk):
    variant = get_object_or_404(JewelleryVariant, pk=pk)
    if request.method == 'POST':
        form = JewelleryVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Variant for {variant.jewellery.name} updated.")
            return redirect('catalogue:ims_variant_list')
    else:
        form = JewelleryVariantForm(instance=variant)
    return render(request, 'ims/variant_form.html', {'form': form, 'title': 'Edit Variation', 'variant': variant})

@staff_required
def ims_variant_delete(request, pk):
    variant = get_object_or_404(JewelleryVariant, pk=pk)
    if request.method == 'POST':
        name = str(variant)
        variant.delete()
        messages.success(request, f"Variant {name} deleted.")
        return redirect('catalogue:ims_variant_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': variant, 'title': 'Delete Variation', 'back_url': 'catalogue:ims_variant_list'
    })


# Categories CRUD
@staff_required
def ims_category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'ims/category_list.html', {'categories': categories})

@staff_required
def ims_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created.")
            return redirect('catalogue:ims_category_list')
    else:
        form = CategoryForm()
    return render(request, 'ims/category_form.html', {'form': form, 'title': 'Add Category'})

@staff_required
def ims_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('catalogue:ims_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'ims/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})

@staff_required
def ims_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('catalogue:ims_category_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': category, 'title': 'Delete Category', 'back_url': 'catalogue:ims_category_list'
    })


# Collections CRUD
@staff_required
def ims_collection_list(request):
    collections = Collection.objects.all().order_by('name')
    return render(request, 'ims/collection_list.html', {'collections': collections})

@staff_required
def ims_collection_add(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            collection = form.save()
            messages.success(request, f"Collection '{collection.name}' created.")
            return redirect('catalogue:ims_collection_list')
    else:
        form = CollectionForm()
    return render(request, 'ims/collection_form.html', {'form': form, 'title': 'Add Collection'})

@staff_required
def ims_collection_edit(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, f"Collection '{collection.name}' updated.")
            return redirect('catalogue:ims_collection_list')
    else:
        form = CollectionForm(instance=collection)
    return render(request, 'ims/collection_form.html', {'form': form, 'title': 'Edit Collection', 'collection': collection})

@staff_required
def ims_collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        name = collection.name
        collection.delete()
        messages.success(request, f"Collection '{name}' deleted.")
        return redirect('catalogue:ims_collection_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': collection, 'title': 'Delete Collection', 'back_url': 'catalogue:ims_collection_list'
    })

# --- Variations ---

@staff_required
def ims_variant_list(request):
    variants = JewelleryVariant.objects.all().select_related('jewellery', 'image')
    return render(request, 'ims/variant_list.html', {'variants': variants})

@staff_required
def ims_variant_add(request):
    if request.method == 'POST':
        form = JewelleryVariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save()
            messages.success(request, f"Variant for '{variant.jewellery.name}' added successfully.")
            return redirect('catalogue:ims_variant_list')
    else:
        form = JewelleryVariantForm()
    return render(request, 'ims/variant_form.html', {'form': form, 'title': 'Add New Variant'})

@staff_required
def ims_variant_edit(request, pk):
    variant = get_object_or_404(JewelleryVariant, pk=pk)
    if request.method == 'POST':
        form = JewelleryVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Variant for '{variant.jewellery.name}' updated.")
            return redirect('catalogue:ims_variant_list')
    else:
        form = JewelleryVariantForm(instance=variant)
    return render(request, 'ims/variant_form.html', {'form': form, 'title': 'Edit Variant'})

@staff_required
def ims_variant_delete(request, pk):
    variant = get_object_or_404(JewelleryVariant, pk=pk)
    if request.method == 'POST':
        name = str(variant)
        variant.delete()
        messages.success(request, f"Variant '{name}' deleted.")
        return redirect('catalogue:ims_variant_list')
    return render(request, 'ims/confirm_delete.html', {
        'object': variant, 'title': 'Delete Variant', 'back_url': 'catalogue:ims_variant_list'
    })
