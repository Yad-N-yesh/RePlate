"""
ASGI config for toogoodtoosave project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""


#ASGI = Asynchronous Server Gateway Interface
import os #Python's built-in module for working with the operating system

from django.core.asgi import get_asgi_application #a function provided by django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toogoodtoosave.settings')
#If the Django settings module hasn't already been set, use toogoodtosave.settings as the default.

application = get_asgi_application()
#creates djangos ASGI application ->
#the ASGI server looks for this application object to communicate with your Django project.
