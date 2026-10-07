from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),

    # Customer
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
   path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/password_reset_email.html',
        success_url='/password-reset/done/'
    ),
    name='password_reset'
),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),name='password_reset_done'),
    path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url='/reset/done/'
    ),
    name='password_reset_confirm'
),    
    path(
    'reset/done/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ),
    name='password_reset_complete'
),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/orders/', views.order_history, name='order_history'),

    # Seller
    path('seller/register/', views.seller_register, name='seller_register'),
    path('seller/login/', views.seller_login, name='seller_login'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/add/', views.product_add, name='product_add'),
    path('seller/products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('seller/products/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    # Products / ordering (shared)
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/order/', views.place_order, name='place_order'),
]
