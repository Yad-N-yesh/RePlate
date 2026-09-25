"""
URL configuration for toogoodtoosave project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings #from dango find conf and Get Django's project settings to use them in this file
from django.conf.urls.static import static #from dango go deep in conf then urls then statis and import static
from django.contrib import admin
from django.urls import include, path
#include():Go to another URL file and let that file handle the URLs.
#path:used to create a url rule (ex:/admin/ directs to admin web)


#it is a list of many urls
urlpatterns = [
    path('admin/', admin.site.urls), #opens admin url on /admin/
    path('', include('core.urls')), #For the main website URLs, let core/urls.py handle them.
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ##Connect media URL to the media storage folder.