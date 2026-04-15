from django.urls import path
from .views import ListeVendeursAPI, ListeComptablesAPI

urlpatterns = [
    path('vendeurs/', ListeVendeursAPI.as_view(), name='api-vendeurs'),
    path('comptables/', ListeComptablesAPI.as_view(), name='api-comptables'),
]
