from django.urls import path,include
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter

from app.viewsets import *

# Create a router and register our viewsets with it.
router = DefaultRouter()


router.register(r'',DefaultViewSet)
router.register(r'user',UserViewSet)
# router.register(r'reservation',ReservationViewSet)


urlpatterns = [
    path('',include(router.urls)),
]