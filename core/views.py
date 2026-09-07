from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import customer_required, seller_required
from .forms import (
    CustomerRegisterForm, LoginForm, OrderForm, ProductForm, SellerRegisterForm,
)
from .models import CustomerProfile, Order, Product, SellerProfile


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

def home(request):
    """Landing page: shows a preview of live listings + search box."""
    query = request.GET.get('q', '').strip()

    products = Product.objects.filter(
        is_active=True, quantity_available__gt=0
    ).select_related('seller').order_by('expiry_date')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query) |
            Q(seller__shop_name__icontains=query)
        )

    # Only ever show non-expired items to customers.
    products = [p for p in products if not p.is_expired()][:24]

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'core/home.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('core:home')


# ---------------------------------------------------------------------------
# Customer auth
# ---------------------------------------------------------------------------

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'], email=data.get('email', ''),
                password=data['password'],
            )
            CustomerProfile.objects.create(
                user=user,
                phone_number=data.get('phone_number', ''),
                address=data.get('address', ''),
            )
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your customer account was created.")
            return redirect('core:customer_dashboard')
    else:
        form = CustomerRegisterForm()
    return render(request, 'core/customer_register.html', {'form': form})


def customer_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and hasattr(user, 'customer_profile'):
                login(request, user)
                return redirect('core:customer_dashboard')
            messages.error(request, "Invalid customer credentials.")
    else:
        form = LoginForm()
    return render(request, 'core/customer_login.html', {'form': form})


# ---------------------------------------------------------------------------
# Seller auth
# ---------------------------------------------------------------------------

def seller_register(request):
    if request.method == 'POST':
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'], email=data.get('email', ''),
                password=data['password'],
            )
            SellerProfile.objects.create(
                user=user,
                shop_name=data['shop_name'],
                phone_number=data.get('phone_number', ''),
                address=data.get('address', ''),
            )
            login(request, user)
            messages.success(request, f"Welcome, {data['shop_name']}! Your seller account was created.")
            return redirect('core:seller_dashboard')
    else:
        form = SellerRegisterForm()
    return render(request, 'core/seller_register.html', {'form': form})


def seller_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and hasattr(user, 'seller_profile'):
                login(request, user)
                return redirect('core:seller_dashboard')
            messages.error(request, "Invalid seller credentials.")
    else:
        form = LoginForm()
    return render(request, 'core/seller_login.html', {'form': form})


# ---------------------------------------------------------------------------
# Customer dashboard / browsing / ordering
# ---------------------------------------------------------------------------

@customer_required
def customer_dashboard(request):
    profile = request.user.customer_profile
    orders = profile.orders.select_related('product', 'seller').order_by('-created_at')[:10]
    return render(request, 'core/customer_dashboard.html', {'orders': orders})


def product_list(request):
    """Browse + search all live listings (open to everyone, ordering requires login)."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.filter(
        is_active=True, quantity_available__gt=0
    ).select_related('seller').order_by('expiry_date')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(seller__shop_name__icontains=query)
        )
    if category:
        products = products.filter(category=category)

    products = [p for p in products if not p.is_expired()]

    context = {
        'products': products,
        'query': query,
        'category': category,
        'categories': Product.CATEGORY_CHOICES,
    }
    return render(request, 'core/product_list.html', context)


@customer_required
def place_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if not product.is_available():
        messages.error(request, "Sorry, this item is no longer available.")
        return redirect('core:product_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity > product.quantity_available:
                messages.error(request, "Not enough stock left for that quantity.")
                return redirect('core:place_order', product_id=product.id)

            unit_price = product.discounted_price
            commission_total = product.commission_amount() * quantity
            seller_earning_total = product.seller_earning_per_unit() * quantity
            total_price = unit_price * quantity

            order = Order.objects.create(
                customer=request.user.customer_profile,
                product=product,
                seller=product.seller,
                quantity=quantity,
                unit_price=unit_price,
                commission_amount_total=commission_total,
                seller_earning_total=seller_earning_total,
                total_price=total_price,
                disclaimer_accepted=form.cleaned_data['disclaimer_accepted'],
            )

            product.quantity_available -= quantity
            if product.quantity_available <= 0:
                product.is_active = False
            product.save()

            messages.success(request, "Order placed! Please pick it up within the seller's pickup window.")
            return redirect('core:order_history')
    else:
        form = OrderForm()

    return render(request, 'core/order_confirm.html', {'product': product, 'form': form})


@customer_required
def order_history(request):
    orders = request.user.customer_profile.orders.select_related(
        'product', 'seller'
    ).order_by('-created_at')
    return render(request, 'core/order_history.html', {'orders': orders})


# ---------------------------------------------------------------------------
# Seller dashboard / product management
# ---------------------------------------------------------------------------

@seller_required
def seller_dashboard(request):
    seller = request.user.seller_profile
    products = seller.products.order_by('-created_at')
    sales = seller.sales.select_related('product', 'customer').order_by('-created_at')[:20]

    total_earnings = sum((s.seller_earning_total for s in seller.sales.all()), Decimal('0'))
    total_commission_paid = sum((s.commission_amount_total for s in seller.sales.all()), Decimal('0'))

    context = {
        'products': products,
        'sales': sales,
        'total_earnings': total_earnings,
        'total_commission_paid': total_commission_paid,
        'commission_percent': settings.PLATFORM_COMMISSION_PERCENT,
    }
    return render(request, 'core/seller_dashboard.html', context)


@seller_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller_profile
            product.commission_percent = settings.PLATFORM_COMMISSION_PERCENT
            product.save()
            messages.success(request, "Product listed successfully.")
            return redirect('core:seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'mode': 'add'})


@seller_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user.seller_profile)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect('core:seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'mode': 'edit', 'product': product})


@seller_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id, seller=request.user.seller_profile)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product removed.")
    return redirect('core:seller_dashboard')
