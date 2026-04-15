from rest_framework import serializers
from suivi.models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'nom', 'prenom', 'is_cadre', 'is_vendeur', 'is_comptable']
