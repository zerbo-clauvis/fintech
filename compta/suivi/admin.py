# suivi/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class UtilisateurAdmin(UserAdmin):
    # On ajoute nos nouveaux champs dans l'affichage de l'admin
    fieldsets = UserAdmin.fieldsets + (
        ('Rôles spécifiques', {'fields': ('is_cadre', 'is_vendeur', 'is_comptable')}),
    )

admin.site.register(Utilisateur, UtilisateurAdmin)
