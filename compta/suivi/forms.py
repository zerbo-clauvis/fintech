from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur
from django import forms
from .models import Entreprise



class UtilisateurCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('vendeur', 'Vendeur'),
        ('comptable', 'Comptable'),
        ('cadre', 'Cadre'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Rôle")
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all(), label="Entreprise")

    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entreprise'].widget = forms.HiddenInput()

class EntrepriseEtUtilisateurForm(forms.Form):
    
    nom_entreprise = forms.CharField(max_length=100, label="Nom de l'Entreprise")
    
   
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    ROLE_CHOICES = [
        ('cadre', 'Cadre'),
        ('vendeur', 'Vendeur'),
        ('comptable', 'Comptable'),
        
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Rôle")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data 

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom_entreprise']