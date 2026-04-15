from datetime import datetime, date, timedelta
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import ValidationError
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from .forms import EntrepriseForm, UtilisateurCreationForm, EntrepriseEtUtilisateurForm
from django.contrib.auth.hashers import make_password

def est_cadre(user):
    return user.is_authenticated and user.is_cadre

def est_vendeur(user):
    return user.is_authenticated and user.is_vendeur

def est_comptable(user):
    return user.is_authenticated and user.is_comptable


def home(request):   
    return render(request, 'home.html')   
   

@user_passes_test(est_cadre)
def gestion_roles(request):
    utilisateurs = Utilisateur.objects.filter(entreprise=request.user.entreprise)
    return render(request, 'gestion_roles.html', {'utilisateurs': utilisateurs})


@user_passes_test(est_cadre)
def modifier_statut(request, user_id):

    if request.method == "POST":
        target_user = get_object_or_404(Utilisateur, id=user_id)
        
     
        nouveau_role = request.POST.get('role')

        target_user.is_vendeur = False
        target_user.is_comptable = False
        target_user.is_cadre = False

     
        if nouveau_role == 'vendeur':
            target_user.is_vendeur = True
        elif nouveau_role == 'comptable':
            target_user.is_comptable = True
        elif nouveau_role == 'cadre':
            target_user.is_cadre = True
        
        target_user.save()
        
    return redirect('gestion_roles') 




def entreprise(request):
    if request.method == 'POST':
        form = EntrepriseEtUtilisateurForm(request.POST)
        if form.is_valid():
            
            nom_entreprise = form.cleaned_data['nom_entreprise']
            entreprise = Entreprise.objects.create(nom_entreprise=nom_entreprise)
            
            
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            role = form.cleaned_data['role']
            
            user = Utilisateur.objects.create_user(
                username=username,
                email=email,
                password=password,
                entreprise=entreprise
             
            )
            
            if role == 'vendeur':
                user.is_vendeur = True
            elif role == 'comptable':
                user.is_comptable = True
            elif role == 'cadre':
                user.is_cadre = True
            user.save()
            
            messages.success(request, f'Entreprise "{nom_entreprise}" et utilisateur "{username}" créés avec succès!')
            return redirect('connexion')
    else:
        form = EntrepriseEtUtilisateurForm()
    return render(request, 'entreprise.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST.get('username') 
        mdp = request.POST.get('password') 

        
        user = authenticate(request, username=nom_utilisateur, password=mdp)

        if user is not None:
            login(request, user)
            return redirect('vente')  
        else:
            
            return render(request, 'connexion.html', {'error': 'Identifiants incorrects'})
            
    return render(request, 'connexion.html')



@user_passes_test(est_cadre)



def creer_utilisateur(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        role = request.POST.get("role")

        user = Utilisateur(
            username=username,
            email=email,
            password=make_password(password1),
            entreprise=request.user.entreprise
        )

     
        user.is_cadre = False
        user.is_vendeur = False
        user.is_comptable = False

        if role == "cadre":
            user.is_cadre = True
        elif role == "vendeur":
            user.is_vendeur = True
        elif role == "comptable":
            user.is_comptable = True

        user.save()

        messages.success(request, "Utilisateur créé avec succès 👍")
        return redirect("creer_utilisateur")

    return render(request, "utilisateur.html")

@user_passes_test(est_cadre)
def dashboard(request):
    return render(request, 'dashboard.html')

@user_passes_test(est_comptable or est_cadre)
def tresorerie(request):
    return render(request, 'tresorerie.html')

def produit(request):
    if request.method == 'POST':
        print("POST reçu :", request.POST)
        produit= Produit (
        nom_produit = request.POST.get('nom_produit'),       
        quantite = request.POST.get('quantite'),
        entreprise = request.user.entreprise

        )
        produit.save()     
    return render(request, 'dashboard.html')

def budget(request):
    if request.method == 'POST':
        nom_budget = request.POST.get('nom_budget')
        montant_budget = request.POST.get('montant_budget')
        entreprise = request.user.entreprise
        Budget.objects.create(nom_budget=nom_budget, montant_budget=montant_budget, entreprise=entreprise)
    return render(request, 'dashboard.html')

def fournisseur(request):
    if request.method == 'POST':
        nom_fournisseur = request.POST.get('nom_fournisseur')
        entreprise = request.user.entreprise
        Fournisseur.objects.create(nom_fournisseur=nom_fournisseur, entreprise=entreprise)
    return render(request, 'dashboard.html')

@login_required
def vente(request):
   if request.method == 'POST':
    nom = request.POST.get('nom_vente')
    entreprise = request.user.entreprise
    
    try:
       
       
        produit_trouve = Produit.objects.get(nom_produit=nom, entreprise=entreprise)
        if produit_trouve.quantite < int(request.POST.get('quantite_vendue')):
            return HttpResponse("Quantité insuffisante en stock !")
        produit_trouve.quantite -= int(request.POST.get('quantite_vendue'))
      
        produit_trouve.save()
        
        Vente.objects.create(
            produit = produit_trouve,
            prix_vente = request.POST.get('prix_vente'),
            quantite_vendue = request.POST.get('quantite_vendue'),
            entreprise = entreprise
        )
    except Produit.DoesNotExist:
       
        return HttpResponse("Produit non trouvé !")

    return render(request, 'vente.html')

   return render(request, 'vente.html')

@user_passes_test(est_comptable or est_cadre)
def achat(request):
    budgets = Budget.objects.filter(entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        budget_id = request.POST.get('budget')
        nom_achat = request.POST.get('nom_achat')
        prix_achat = request.POST.get('prix_achat')
        entreprise = request.user.entreprise
        
        try:
          
            budget = Budget.objects.get(id=budget_id)
            
            prix_achat = float(prix_achat)
            
            
            achat = Achat(
                budget=budget,
                nom_achat=nom_achat,
                prix_achat=prix_achat,
                entreprise=entreprise

            )
            
           
            achat.save()
            messages.success(request, f'Achat "{nom_achat}" enregistré avec succès ! Budget restant: {budget.montant_budget}€')
            
        except Budget.DoesNotExist:
            messages.error(request, 'Budget sélectionné introuvable.')
        except ValidationError as e:
            messages.error(request, str(e))
        except ValueError:
            messages.error(request, 'Le prix doit être un nombre valide.')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    return render(request, 'achat.html', {'budgets': budgets})    


def dette(request):
    fournisseurs = Fournisseur.objects.filter(entreprise=request.user.entreprise)
  
    search_query = request.GET.get('search_fournisseur', '').strip()

    dettes = Dette.objects.select_related('nom_fournisseur').filter(entreprise=request.user.entreprise)
    if search_query:
        dettes = dettes.filter(nom_fournisseur__nom_fournisseur__icontains=search_query)

    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'update':
            nom_dette_update = request.POST.get('nom_dette_update')
            montant_paye_update = request.POST.get('montant_paye_update')
            try:
                dette_existante = Dette.objects.filter(nom_dette=nom_dette_update).first()
                if not dette_existante:
                    messages.error(request, f"Aucune dette trouvée pour le nom '{nom_dette_update}'.")
                else:
                    dette_existante.montant_paye += float(montant_paye_update or 0)
                    dette_existante.save()
                    messages.success(request, f"Dette '{nom_dette_update}' mise à jour. Montant restant : {dette_existante.montant_restant}.")
            except ValueError:
                messages.error(request, "Valeurs numériques invalides pour le montant payé.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour de la dette : {e}")

        else:
            nom_dette = request.POST.get('nom_dette')
            fournisseur_id = request.POST.get('nom_fournisseur')
            montant_dette = request.POST.get('montant_dette')
            montant_paye = request.POST.get('montant_paye')

            try:
                fournisseur = get_object_or_404(Fournisseur, id=int(fournisseur_id))
                dette = Dette(
                    nom_dette=nom_dette,
                    nom_fournisseur=fournisseur,
                    montant_dette=float(montant_dette or 0),
                    montant_paye=float(montant_paye or 0),
                )
                dette.save()
                messages.success(request, "Dette enregistrée avec succès. Montant restant calculé automatiquement.")
                dettes = Dette.objects.select_related('nom_fournisseur').all()
            except ValueError:
                messages.error(request, "Valeurs numériques invalides pour la dette ou le montant payé.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de la dette : {e}")

    return render(request, 'gestiondette.html', {
        'fournisseurs': fournisseurs,
        'dettes': dettes,
        'search_query': search_query,
    })

def gestion_stock(request):
    produits = Produit.objects.filter(entreprise=request.user.entreprise).order_by('nom_produit')

    if request.method == 'POST':
        action = request.POST.get('action', 'create')
        if action == 'create':
            nom_produit = request.POST.get('nom_produit')
            quantite = request.POST.get('quantite')
            entreprise = request.user.entreprise
            try:
                quantite_val = int(quantite or 0)
                if not nom_produit:
                    raise ValueError("Le nom du produit est requis.")
                Produit.objects.create(nom_produit=nom_produit, quantite=quantite_val, entreprise=entreprise)
                messages.success(request, f"Produit '{nom_produit}' ajouté avec {quantite_val} unités.")
            except ValueError as e:
                messages.error(request, f"Erreur création produit : {e}")
        elif action == 'update':
            produit_id = request.POST.get('produit_id')
            quantite_ajout = request.POST.get('quantite_ajout')
            try:
                quantite_val = int(quantite_ajout or 0)
                produit = get_object_or_404(Produit, id=int(produit_id))
                produit.quantite = max(0, produit.quantite + quantite_val)
                produit.save()
                messages.success(request, f"Stock mis à jour pour '{produit.nom_produit}'. Quantité restante : {produit.quantite}.")
            except ValueError:
                messages.error(request, "Quantité invalide pour la mise à jour.")
            except Exception as e:
                messages.error(request, f"Erreur mise à jour stock : {e}")

        produits = Produit.objects.filter(entreprise = request.user.entreprise).order_by('nom_produit')

    return render(request, 'gestionstock.html', {
        'produits': produits,
    })

def dette_interne (request):
    dettes_internes = Detteinterne.objects.filter(entreprise=request.user.entreprise)

    if request.method == 'POST':
        nom_dette_interne = request.POST.get('nom_dette_interne')
        creantier = request.POST.get('creantier')
        montant_paye_interne = request.POST.get('montant_paye_interne')
        entreprise = request.user.entreprise
        
        if nom_dette_interne:
          
            dette_interne = Detteinterne(
                date=request.POST.get('date'),
                nom_dette_interne=nom_dette_interne,
                creantier=creantier,
                montant_dette_interne=request.POST.get('montant_dette_interne'),
                montant_paye_interne=montant_paye_interne,
                entreprise=entreprise
            )
            dette_interne.save()
            messages.success(request, "Nouvelle dette interne créée.")
        elif creantier:
          
            dette_existante = Detteinterne.objects.filter(creantier=creantier).first()
            if dette_existante:
                try:
                    montant_paye_val = float(montant_paye_interne or 0)
                except ValueError:
                    montant_paye_val = 0
                dette_existante.montant_paye_interne += montant_paye_val
                dette_existante.save()
                messages.success(request, f"Dette mise à jour pour {creantier}. Montant restant: {dette_existante.montant_restant_interne}")
            else:
                messages.error(request, f"Aucune dette trouvée pour le créancier {creantier}.")
        else:
            messages.error(request, "Veuillez fournir un nom de dette pour créer ou un créancier pour mettre à jour.")
        
        dettes_internes = Detteinterne.objects.all() 
    
    return render(request, 'dette_interne.html', {'dettes_internes': dettes_internes})


def rapport(request):
    mode = request.GET.get('mode', 'jour')
    periode = request.GET.get('periode', '')

    ventes = Vente.objects.filter(entreprise=request.user.entreprise)
    achats = Achat.objects.filter(entreprise=request.user.entreprise)
    dettes = Dette.objects.filter(entreprise=request.user.entreprise)
    dettes_internes = Detteinterne.objects.filter(entreprise=request.user.entreprise)
    periode_label = 'Toutes les dates'

    if mode == 'mois':
        if periode:
            try:
                periode_date = datetime.strptime(periode, '%Y-%m').date()
            except ValueError:
                periode_date = date.today().replace(day=1)
        else:
            periode_date = date.today().replace(day=1)

        start = periode_date.replace(day=1)
        next_month = (start + timedelta(days=32)).replace(day=1)
        ventes = ventes.filter(date__gte=start, date__lt=next_month)
        achats = achats.filter(date__gte=start, date__lt=next_month)
        dettes = dettes.filter(date__gte=start, date__lt=next_month)
        dettes_internes = dettes_internes.filter(date__gte=start, date__lt=next_month)
        periode_label = f"Mois de {start.strftime('%Y-%m')}"

    else:
      
        if periode:
            try:
                jour = datetime.strptime(periode, '%Y-%m-%d').date()
            except ValueError:
                jour = date.today()
        else:
            jour = date.today()

        ventes = ventes.filter(date=jour)
        achats = achats.filter(date=jour)
        dettes = dettes.filter(date=jour)
        dettes_internes = dettes_internes.filter(date=jour)
        periode_label = f"Jour : {jour.strftime('%Y-%m-%d')}"

    ventes = ventes.annotate(total_vente=F('prix_vente') * F('quantite_vendue'))
    total_ventes = ventes.aggregate(total=Sum('total_vente'))['total'] or 0
    total_achats = achats.aggregate(total=Sum('prix_achat'))['total'] or 0
    total_dettes = dettes.aggregate(total=Sum('montant_restant'))['total'] or 0
    total_dettes_internes = dettes_internes.aggregate(total=Sum('montant_restant_interne'))['total'] or 0

    context = {
        'mode': mode,
        'periode': periode,
        'periode_label': periode_label,
        'ventes': ventes,
        'achats': achats,
        'dettes': dettes,
        'dettes_internes': dettes_internes,
        'total_ventes': total_ventes,
        'total_achats': total_achats,
        'total_dettes': total_dettes,
        'total_dettes_internes': total_dettes_internes,
        'total_global': total_ventes - total_achats - total_dettes - total_dettes_internes,
    }

    return render(request, 'rapport.html', context)

