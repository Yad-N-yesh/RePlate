from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'customer_profile'):
            messages.error(request, "Please log in as a customer to continue.")
            return redirect('core:customer_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'seller_profile'):
            messages.error(request, "Please log in as a seller to continue.")
            return redirect('core:seller_login')
        return view_func(request, *args, **kwargs)
    return wrapper
