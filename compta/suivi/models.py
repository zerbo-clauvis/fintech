from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from django.db.models import Sum, F
from datetime import date
from django.contrib.auth.models import AbstractUser
    
class Entreprise(models.Model):
    id = models.AutoField(primary_key=True)
    nom_entreprise = models.CharField(max_length=100, default="entreprise")

class Utilisateur(AbstractUser):
    is_cadre = models.BooleanField(default=True)
    is_vendeur = models.BooleanField(default=False)
    is_comptable = models.BooleanField(default=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

class Budget(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_budget= models.CharField(max_length=100, null=True, blank=True)
    montant_budget = models.FloatField(null=True, blank=True)    
    
class Produit(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_produit= models.CharField(max_length=100)
    quantite = models.IntegerField(default=0)

   
class Vente(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    produit= models.ForeignKey(Produit, on_delete=models.CASCADE)
    prix_vente = models.FloatField()
    quantite_vendue = models.IntegerField()
   

    @property
    def rapport_journalier():
        aujourd_hui = date.today()

        ventes = Vente.objects.filter(date=aujourd_hui)

        total = ventes.aggregate(
            total=Sum(F('prix_vente') * F('quantite_vendue'))
        )

        return {
            "ventes": ventes,
            "total": total["total"] or 0
        }

    @staticmethod
    def rapport_mensuel(mois=None, annee=None):
        if mois is None or annee is None:
            aujourd_hui = date.today()
            mois = aujourd_hui.month
            annee = aujourd_hui.year

        start_date = date(annee, mois, 1)
        if mois == 12:
            end_date = date(annee + 1, 1, 1)
        else:
            end_date = date(annee, mois + 1, 1)

        ventes = Vente.objects.filter(date__gte=start_date, date__lt=end_date)

        total = ventes.aggregate(
            total=Sum(F('prix_vente') * F('quantite_vendue'))
        )

        return {
            "ventes": ventes,
            "total": total["total"] or 0,
            "mois": mois,
            "annee": annee
        }
      

class Achat(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    nom_achat= models.CharField(max_length=100)
    prix_achat = models.IntegerField()

    def save(self, *args, **kwargs):
       
        if self.prix_achat > self.budget.montant_budget:
            raise ValidationError("Le montant du budget est insuffisant !")

        self.budget.montant_budget -= self.prix_achat
        self.budget.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_achat} "


class Fournisseur(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_fournisseur= models.CharField(max_length=100)
   

class Dette(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    nom_dette = models.CharField(max_length=100)
    nom_fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    montant_dette = models.FloatField()
    montant_paye = models.FloatField()
    montant_restant = models.FloatField()

    def save(self, *args, **kwargs):
        try:
            montant_dette_val = float(self.montant_dette)
        except (TypeError, ValueError):
            montant_dette_val = 0.0

        try:
            montant_paye_val = float(self.montant_paye)
        except (TypeError, ValueError):
            montant_paye_val = 0.0

        self.montant_dette = montant_dette_val
        self.montant_paye = montant_paye_val
        reste = montant_dette_val - montant_paye_val
        self.montant_restant = reste if reste >= 0 else 0.0
        super().save(*args, **kwargs)

class Detteinterne(models.Model):
    id = models.AutoField(primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    nom_dette_interne = models.CharField(max_length=100)
    creantier = models.CharField(max_length=100, null=True, blank=True)
    montant_dette_interne = models.FloatField()
    montant_paye_interne = models.FloatField()
    montant_restant_interne = models.FloatField()

    def save(self, *args, **kwargs):
        try:
            montant_dette_val = float(self.montant_dette_interne)
        except (TypeError, ValueError):
            montant_dette_val = 0.0

        try:
            montant_paye_val = float(self.montant_paye_interne)
        except (TypeError, ValueError):
            montant_paye_val = 0.0

        self.montant_dette_interne = montant_dette_val
        self.montant_paye_interne = montant_paye_val
        reste = montant_dette_val - montant_paye_val
        self.montant_restant_interne = reste if reste >= 0 else 0.0
        super().save(*args, **kwargs)

