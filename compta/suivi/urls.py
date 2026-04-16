from django.urls import path
from . import views



urlpatterns = [
    path('achat/',views.achat, name = 'achat'),
    path('vente/',views.vente, name = 'vente'),
    path('dette/',views.dette, name = 'dette'),
    path('connexion/', views.connexion, name='connexion'),
    path('entreprise/', views.entreprise, name='entreprise'),
    path('utilisateur/', views.creer_utilisateur, name='creer_utilisateur'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('produit/', views.produit, name='produit'),
    path('budget/', views.budget, name='budget'),
    path('fournisseur/', views.fournisseur, name='fournisseur'), 
    path('tresorerie/', views.tresorerie, name='tresorerie'),
    path('detteinterne/', views.dette_interne, name='detteinterne'),
    path('gestionstock/', views.gestion_stock, name='gestionstock'),
    path('rapport/', views.rapport, name='rapport'),
    path('modifier-statut/<int:user_id>/', views.modifier_statut, name='modifier_statut'),
    path('gestion-role/', views.gestion_roles, name='gestion_roles'),
    path('supprimer-produit/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('', views.home, name='home'),
]