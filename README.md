# RePlate — Surplus Food Marketplace (Django)

A "TooGoodToGo"-style marketplace: sellers list packed food items nearing
their expiry date at a discount; customers browse/search and order them,
after accepting a mandatory expiry-risk disclaimer. The platform takes a
commission on every sale — visible only in the seller dashboard, never to
the customer.

## Features

- Separate **Customer** and **Seller** signup/login (two distinct auth flows,
  same Django `User` model, differentiated by a `CustomerProfile` /
  `SellerProfile` one-to-one profile).
- **Home page** with live/near-expiry deals + a search box.
- **Customer dashboard**: recent orders, quick links to browse/search.
- **Seller dashboard**: manage listings (add/edit/delete), see sales, and see
  **net earnings after commission** — the commission % and amount is only
  ever rendered in seller-facing templates/views.
- **Product search & browse** page with category filter.
- **Order flow**: viewing a product's order page pops a **mandatory
  disclaimer modal** ("read & accept before you can order") warning that the
  item is close to expiry, that the buyer must eat/use it before the printed
  expiry date, and that the platform/seller are not responsible for any
  aftermath of consuming it after that date. The "Place Order" button is
  disabled until the disclaimer is accepted, and the server independently
  re-validates `disclaimer_accepted` before creating the `Order` — so it
  can't be bypassed by disabling JavaScript.
- SQLite database (Django default), via the ORM — no raw SQL needed.

## Project structure

```
toogoodtoosave/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # created after migrate
├── toogoodtoosave/             # project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── core/                       # the single app holding all functionality
│   ├── models.py               # CustomerProfile, SellerProfile, Product, Order
│   ├── forms.py                # registration / login / product / order forms
│   ├── views.py                # all page views
│   ├── urls.py                 # core: namespaced routes
│   ├── decorators.py           # @customer_required / @seller_required
│   ├── admin.py                # Django admin registrations
│   ├── migrations/
│   └── templates/core/
│       ├── base.html
│       ├── home.html
│       ├── customer_login.html / customer_register.html
│       ├── seller_login.html / seller_register.html
│       ├── customer_dashboard.html
│       ├── seller_dashboard.html
│       ├── product_list.html        # browse/search
│       ├── product_form.html        # seller add/edit
│       ├── order_confirm.html       # order page + disclaimer modal
│       └── order_history.html
├── static/core/css/style.css
└── media/products/             # uploaded product images (created at runtime)
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 manage.py migrate
python3 manage.py createsuperuser   # optional, for /admin/
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

- `/customer/register/` and `/customer/login/` — customer auth
- `/seller/register/` and `/seller/login/` — seller auth
- `/customer/dashboard/` and `/seller/dashboard/` — role dashboards
- `/products/` — browse & search listings
- `/products/<id>/order/` — order a product (disclaimer required)
- `/admin/` — Django admin (superuser only)

## Commission logic

`PLATFORM_COMMISSION_PERCENT` in `settings.py` (default `10`) is stamped onto
each `Product` at creation time (`Product.commission_percent`), so past
listings/orders keep their original commission even if the site-wide default
changes later. `Product.commission_amount()` / `seller_earning_per_unit()`
compute the split; only `seller_dashboard.html` and the seller-facing admin
list display these numbers. Customer-facing templates (`home.html`,
`product_list.html`, `order_confirm.html`, `order_history.html`,
`customer_dashboard.html`) only ever show `discounted_price` / `total_price`.

## Notes / next steps for production

- Set `DEBUG = False`, add a real `SECRET_KEY` via environment variable, and
  set `ALLOWED_HOSTS` for your domain.
- Swap SQLite for Postgres for concurrent production traffic.
- Add email/SMS verification, password reset, and payment gateway integration.
- Add automated tests (`core/tests.py` is scaffolded and ready to fill in).
