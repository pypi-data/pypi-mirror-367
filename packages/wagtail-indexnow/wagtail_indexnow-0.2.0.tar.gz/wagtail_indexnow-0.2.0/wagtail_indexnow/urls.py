from django.urls import path

from .views import KeyView

urlpatterns = [path("indexnow-<key>.txt", KeyView.as_view())]
