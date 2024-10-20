from django.urls import path

from .views import get_url_info_view

urlpatterns = [
    path("", get_url_info_view),
]