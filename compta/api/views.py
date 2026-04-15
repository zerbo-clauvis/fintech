from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from suivi.models import Utilisateur
from .serializers import UtilisateurSerializer

# Vue pour voir UNIQUEMENT les vendeurs
class ListeVendeursAPI(generics.ListAPIView):
    serializer_class = UtilisateurSerializer
    
    def get_queryset(self):
        return Utilisateur.objects.filter(is_vendeur=True)

# Vue pour voir UNIQUEMENT les comptables
class ListeComptablesAPI(generics.ListAPIView):
    serializer_class = UtilisateurSerializer
    
    def get_queryset(self):
        return Utilisateur.objects.filter(is_comptable=True)
