from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.db.models import Count, Q
from django.db.utils import OperationalError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .forms import InscriptionForm
from .models import Atelier, Inscription, SiteConfiguration, ChiffreCle, Expert, Partenaire, HeroCarouselImage, HeroImage, StatsImage, Evenement, EvenementImage
import csv
from collections import OrderedDict
from django.utils import timezone
from django.core.mail import EmailMessage
from .pdf_agenda import generer_agenda_pdf


def is_staff_user(user):
    return user.is_staff


def staff_login_url(request):
    return f"/admin/login/?next={request.path}"


def staff_required(view_func):
    """Require an authenticated staff user for custom gestion views."""
    wrapped = login_required(view_func, login_url=staff_login_url)
    return user_passes_test(is_staff_user, login_url=staff_login_url)(wrapped)


@staff_required
def manage_hero_stats_images(request):
    """Vue pour gérer les images du hero et des statistiques"""
    hero_images_gauche = HeroImage.objects.filter(position='gauche').order_by('ordre', 'date_ajout')
    hero_images_arriere = HeroImage.objects.filter(position='arriere').order_by('ordre', 'date_ajout')
    stats_images = StatsImage.objects.all().order_by('ordre', 'date_ajout')
    carousel_images = HeroCarouselImage.objects.all().order_by('ordre', 'date_ajout')
    
    context = {
        'hero_images_gauche': hero_images_gauche,
        'hero_images_arriere': hero_images_arriere,
        'stats_images': stats_images,
        'carousel_images': carousel_images,
    }
    return render(request, 'inscriptions/manage_hero_stats_images.html', context)


@require_POST
@staff_required
def add_hero_image(request):
    """Ajouter une image hero"""
    titre = request.POST.get('titre', '')
    image_url = request.POST.get('image_url', '')
    position = request.POST.get('position', 'gauche')
    ordre = int(request.POST.get('ordre', 0))
    
    if not titre:
        messages.error(request, 'Le titre est obligatoire')
        return redirect('manage_hero_stats_images')
    
    hero_image = HeroImage.objects.create(
        titre=titre,
        image_url=image_url,
        position=position,
        ordre=ordre
    )
    
    # Gérer l'upload de fichier
    if 'image' in request.FILES:
        hero_image.image = request.FILES['image']
        hero_image.save()
    
    messages.success(request, f'Image "{titre}" ajoutée avec succès')
    return redirect('manage_hero_stats_images')


@require_POST
@staff_required
def add_stats_image(request):
    """Ajouter une image statistiques"""
    titre = request.POST.get('titre', '')
    image_url = request.POST.get('image_url', '')
    ordre = int(request.POST.get('ordre', 0))
    
    if not titre:
        messages.error(request, 'Le titre est obligatoire')
        return redirect('manage_hero_stats_images')
    
    stats_image = StatsImage.objects.create(
        titre=titre,
        image_url=image_url,
        ordre=ordre
    )
    
    # Gérer l'upload de fichier
    if 'image' in request.FILES:
        stats_image.image = request.FILES['image']
        stats_image.save()
    
    messages.success(request, f'Image statistiques "{titre}" ajoutée avec succès')
    return redirect('manage_hero_stats_images')


@require_POST
@staff_required
def toggle_hero_image(request, image_id):
    """Activer/désactiver une image hero"""
    image = get_object_or_404(HeroImage, id=image_id)
    image.active = not image.active
    image.save()
    
    status = "activée" if image.active else "désactivée"
    return JsonResponse({'success': True, 'status': status})


@require_POST
@staff_required
def toggle_stats_image(request, image_id):
    """Activer/désactiver une image statistiques"""
    image = get_object_or_404(StatsImage, id=image_id)
    image.active = not image.active
    image.save()
    
    status = "activée" if image.active else "désactivée"
    return JsonResponse({'success': True, 'status': status})


@require_POST
@staff_required
def delete_hero_image(request, image_id):
    """Supprimer une image hero"""
    image = get_object_or_404(HeroImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


@require_POST
@staff_required
def delete_stats_image(request, image_id):
    """Supprimer une image statistiques"""
    image = get_object_or_404(StatsImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


@require_POST
@staff_required
def update_hero_image_order(request):
    """Mettre à jour l'ordre des images hero"""
    orders = request.POST.getlist('orders[]')
    for i, image_id in enumerate(orders):
        try:
            image = HeroImage.objects.get(id=image_id)
            image.ordre = i
            image.save()
        except HeroImage.DoesNotExist:
            continue
    return JsonResponse({'success': True})


@require_POST
@staff_required
def update_stats_image_order(request):
    """Mettre à jour l'ordre des images statistiques"""
    orders = request.POST.getlist('orders[]')
    for i, image_id in enumerate(orders):
        try:
            image = StatsImage.objects.get(id=image_id)
            image.ordre = i
            image.save()
        except StatsImage.DoesNotExist:
            continue
    return JsonResponse({'success': True})


def _get_evenement_payload(edition):
    try:
        ev = Evenement.objects.filter(edition=edition).first()
        objectifs = []
        if ev and ev.objectifs:
            objectifs = [x.strip() for x in ev.objectifs.split('\n') if x.strip()]
        images = []
        if ev:
            images = list(EvenementImage.objects.filter(evenement=ev, active=True).order_by('ordre', 'date_ajout'))
        chiffres_ev = []
        try:
            chiffres_ev = list(ChiffreCle.objects.filter(edition=edition).order_by('ordre'))
        except OperationalError:
            pass
        return {
            'evenement': ev,
            'objectifs': objectifs,
            'images': images,
            'chiffres': chiffres_ev,
        }
    except OperationalError:
        return {
            'evenement': None,
            'objectifs': [],
            'images': [],
            'chiffres': [],
        }


def restitution_page(request):
    """Page de restitution des résultats DounIA"""
    from .models import Restitution, RestitutionImage
    from django.db.models import Q
    
    try:
        restitution = Restitution.objects.get(pk=1)
    except Restitution.DoesNotExist:
        # Créer une instance par défaut si elle n'existe pas
        restitution = Restitution.objects.create(
            mission_points=[
                'Partager les connaissances acquises',
                'Présenter les recommandations concrètes',
                'Faciliter la prise de décision'
            ],
            public_points=[
                'Décideurs politiques',
                'Experts techniques',
                'Société civile',
                'Secteur privé'
            ],
            chronologie=[
                {
                    'date': 'Janvier 2024',
                    'titre': 'Lancement de DounIA 1',
                    'description': 'Démarrage du processus de concertation et des premiers ateliers thématiques.'
                },
                {
                    'date': 'Février - Mars 2024',
                    'titre': 'Ateliers Thématiques',
                    'description': 'Réalisation de 8 ateliers sectoriels avec plus de 150 participants.'
                },
                {
                    'date': 'Avril 2024',
                    'titre': 'Analyse et Synthèse',
                    'description': 'Compilation des résultats et élaboration des recommandations stratégiques.'
                },
                {
                    'date': 'Mai 2024',
                    'titre': 'Restitution Officielle',
                    'description': 'Présentation des résultats et lancement de DounIA 2.'
                }
            ]
        )
    
    stats_images = list(StatsImage.objects.filter(active=True).order_by('ordre', 'date_ajout'))

    context = {
        'page_title': 'Restitution - DounIA',
        'meta_description': 'Restitution des résultats et recommandations des ateliers DounIA',
        'restitution': restitution,
        'stats_images': stats_images,
        'hero_images': list(
            RestitutionImage.objects.filter(
                Q(restitution=restitution) | Q(restitution__isnull=True),
                active=True,
                position='hero',
            ).order_by('ordre', 'date_ajout')
        ),
        'images': list(
            RestitutionImage.objects.filter(
                Q(restitution=restitution) | Q(restitution__isnull=True),
                active=True,
                position='galerie',
            ).order_by('ordre', 'date_ajout')
        ),
    }
    return render(request, 'inscriptions/restitution.html', context)


def get_evenement_data(event_slug):
    """Récupère les données d'un événement depuis le modèle Evenement"""
    try:
        # Utiliser 'edition' au lieu de 'slug' selon le modèle Evenement
        evenement = Evenement.objects.get(edition=event_slug)
        return {
            'evenement': evenement,
            'objectifs': [],  # Simplifié pour éviter les erreurs de relation
            'images': [],     # Simplifié pour éviter les erreurs de relation
            'chiffres': [],   # Simplifié pour éviter les erreurs de relation
        }
    except Evenement.DoesNotExist:
        return {
            'evenement': None,
            'objectifs': [],
            'images': [],
            'chiffres': [],
        }
    except OperationalError:
        return {
            'evenement': None,
            'objectifs': [],
            'images': [],
            'chiffres': [],
        }


def landing_page(request):
    """Page d'accueil avec formulaire d'inscription"""
    form = InscriptionForm()

    config = SiteConfiguration.get()
    
    # Récupérer les événements DounIA
    from .models import DouniaEvent, Restitution
    try:
        dounia1_event = DouniaEvent.objects.get(event_slug='dounia1')
        dounia2_event = DouniaEvent.objects.get(event_slug='dounia2')
        restitution_data = Restitution.objects.get(pk=1)
    except (DouniaEvent.DoesNotExist, Restitution.DoesNotExist):
        dounia1_event = None
        dounia2_event = None
        restitution_data = None
    
    # Récupérer les données existantes
    try:
        chiffres = list(ChiffreCle.objects.all().order_by('ordre'))
    except OperationalError:
        chiffres = []
    
    try:
        experts = Expert.objects.all().order_by('ordre')
    except OperationalError:
        experts = []
    
    try:
        partenaires = Partenaire.objects.all().order_by('ordre')
    except OperationalError:
        partenaires = []

    try:
        partenaires_institutionnels = partenaires.filter(categorie='institutionnel') if hasattr(partenaires, 'filter') else []
        partenaires_techniques = partenaires.filter(categorie='technique') if hasattr(partenaires, 'filter') else []
    except Exception:
        partenaires_institutionnels = []
        partenaires_techniques = []
    
    try:
        hero_images = HeroImage.objects.filter(position='gauche', active=True).order_by('ordre')
    except OperationalError:
        hero_images = []
    
    try:
        stats_images = StatsImage.objects.filter(active=True).order_by('ordre')
    except OperationalError:
        stats_images = []
    
    try:
        hero_bg_images = HeroImage.objects.filter(position='arriere', active=True).order_by('ordre')
    except OperationalError:
        hero_bg_images = []

    bg_images_json = {
        'hero': [img.get_image_url() for img in hero_images],
        'stats': [img.get_image_url() for img in stats_images],
    }
    
    try:
        evenement_dounia1 = get_evenement_data('dounia1')
    except OperationalError:
        evenement_dounia1 = {'evenement': None, 'objectifs': [], 'images': [], 'chiffres': []}
    
    try:
        evenement_dounia2 = get_evenement_data('dounia2')
    except OperationalError:
        evenement_dounia2 = {'evenement': None, 'objectifs': [], 'images': [], 'chiffres': []}
    
    try:
        ateliers_db = Atelier.objects.filter(active=True).order_by('ordre')
        atelier_map = {a.code: {'label': a.label, 'image': a.get_image_url(), 'description': a.description} for a in ateliers_db}
    except OperationalError:
        ateliers_db = []
        atelier_map = {}
    
    context = {
        'form': form,
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'partenaires': partenaires,
        'partenaires_institutionnels': partenaires_institutionnels,
        'partenaires_techniques': partenaires_techniques,
        'ateliers_db': ateliers_db,
        'atelier_map': atelier_map,
        'evenement_dounia1': evenement_dounia1,
        'evenement_dounia2': evenement_dounia2,
        'dounia1_event': dounia1_event,
        'dounia2_event': dounia2_event,
        'restitution_data': restitution_data,
        'hero_images': hero_images,
        'hero_bg_images': hero_bg_images,
        'stats_images': stats_images,
        'bg_images_json': bg_images_json,
    }
    return render(request, 'inscriptions/landing.html', context)


def _landing_context_with_form(form):
    config = SiteConfiguration.get()
    try:
        chiffres = list(ChiffreCle.objects.all().order_by('ordre'))
    except OperationalError:
        chiffres = []
    experts = Expert.objects.all().order_by('ordre')
    partenaires = Partenaire.objects.all().order_by('ordre')
    partenaires_institutionnels = partenaires.filter(categorie='institutionnel')
    partenaires_techniques = partenaires.filter(categorie='technique')
    
    # Utiliser les mêmes images que la landing_page principale
    try:
        hero_images = HeroImage.objects.filter(position='gauche', active=True).order_by('ordre')
    except OperationalError:
        hero_images = []
    
    try:
        stats_images = StatsImage.objects.all().order_by('ordre')
    except OperationalError:
        stats_images = []
    
    try:
        hero_bg_images = HeroImage.objects.filter(position='arriere', active=True).order_by('ordre')
    except OperationalError:
        hero_bg_images = []

    defis = [d.strip() for d in config.dounia1_defis.split('\n') if d.strip()]
    opportunites = [o.strip() for o in config.dounia1_opportunites.split('\n') if o.strip()]
    rapport_points = [p.strip() for p in config.rapport_points.split('\n') if p.strip()]

    phases = []
    for p in [config.dounia2_phase1, config.dounia2_phase2, config.dounia2_phase3, config.dounia2_phase4]:
        parts = p.split('|', 1)
        phases.append({'titre': parts[0].strip(), 'description': parts[1].strip() if len(parts) > 1 else ''})

    bg_images_json = {
        'hero': [img.get_image_url() for img in hero_images],
        'stats': [img.get_image_url() for img in stats_images],
    }

    def _payload_to_dict(payload):
        d = {
            'evenement': {
                'titre': payload['evenement'].titre if payload['evenement'] else None,
                'sous_titre': payload['evenement'].sous_titre if payload['evenement'] else None,
            } if payload['evenement'] else None,
            'objectifs': payload['objectifs'],
            'images': [{'get_image_url': img.get_image_url()} for img in payload['images']],
            'chiffres': [
                {'nombre': c.nombre, 'suffixe': c.suffixe or '', 'label': c.label}
                for c in payload['chiffres']
            ],
        }
        return d

    return {
        'form': form,
        'ateliers': Inscription.ATELIER_CHOICES,
        'atelier_map': atelier_map,
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'partenaires': partenaires,
        'partenaires_institutionnels': partenaires_institutionnels,
        'partenaires_techniques': partenaires_techniques,
        'hero_images': hero_images,
        'hero_bg_images': hero_bg_images,
        'bg_images_json': bg_images_json,
        'defis': defis,
        'opportunites': opportunites,
        'rapport_points': rapport_points,
        'phases': phases,
        'evenement_dounia1': _get_evenement_payload('dounia1'),
        'evenement_dounia2': _get_evenement_payload('dounia2'),
    }


def search_results(request):
    """Vue de recherche qui trouve TOUT le contenu de la landing page"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        query_lower = query.lower()
        print(f"Searching for: {query_lower}")  # Debug
        
        # === CONTENU STATIQUE DE LA LANDING PAGE ===
        
        # Sections principales de la landing page
        sections_content = {
            'hero': {
                'title': 'DounIA - Données Numériques & Intelligence Artificielle',
                'description': 'Première conférence sur les données numériques et l\'intelligence artificielle en Guinée',
                'url': '#hero',
                'keywords': ['dounia', 'données', 'numériques', 'intelligence', 'artificielle', 'guinée', 'conférence']
            },
            'about': {
                'title': 'À propos',
                'description': 'Présentation du projet DounIA et de ses objectifs',
                'url': '#about',
                'keywords': ['projet', 'objectifs', 'présentation', 'dounia']
            },
            'defis': {
                'title': 'Défis',
                'description': 'Les défis de la transformation numérique en Guinée',
                'url': '#dounia1',
                'keywords': ['défis', 'transformation', 'numérique', 'guinée']
            },
            'opportunites': {
                'title': 'Opportunités',
                'description': 'Les opportunités offertes par l\'IA et les données numériques',
                'url': '#dounia1',
                'keywords': ['opportunités', 'intelligence', 'artificielle', 'données']
            },
            'rapport': {
                'title': 'Rapport',
                'description': 'Rapport et points clés du projet DounIA',
                'url': '#livrable',
                'keywords': ['rapport', 'points', 'clés', 'bilan']
            },
            'phases': {
                'title': 'Phases DounIA 2',
                'description': 'Les différentes phases du projet DounIA 2',
                'url': '#dounia2',
                'keywords': ['phases', 'dounia2', 'étapes', 'projet']
            },
            'ateliers': {
                'title': 'Ateliers',
                'description': 'Ateliers pratiques sur les données et l\'IA',
                'url': '#ateliers',
                'keywords': ['ateliers', 'pratique', 'formation', 'données']
            },
            'podcast': {
                'title': 'Podcast',
                'description': 'Podcast sur l\'intelligence artificielle et les données',
                'url': '#podcast',
                'keywords': ['podcast', 'audio', 'intelligence', 'artificielle']
            },
            'partenaires': {
                'title': 'Partenaires',
                'description': 'Nos partenaires institutionnels et techniques',
                'url': '#partenaires',
                'keywords': ['partenaires', 'institutionnel', 'technique', 'collaboration']
            },
            'experts': {
                'title': 'Experts',
                'description': 'Experts intervenants dans le projet DounIA',
                'url': '#experts',
                'keywords': ['experts', 'intervenants', 'spécialistes', 'conférenciers']
            },
            'evenements': {
                'title': 'Événements',
                'description': 'DounIA 1 et DounIA 2 - Les événements principaux',
                'url': '#evenements',
                'keywords': ['événements', 'dounia1', 'dounia2', 'conférence']
            },
            'inscription': {
                'title': 'Inscription',
                'description': 'Formulaire d\'inscription aux événements DounIA',
                'url': '#inscription',
                'keywords': ['inscription', 'formulaire', 'participation', 'inscription']
            }
        }
        
        # Rechercher dans les sections
        for section_key, section_data in sections_content.items():
            score = 0
            search_text = f"{section_data['title']} {section_data['description']} {' '.join(section_data['keywords'])}".lower()
            
            if query_lower in section_data['title'].lower():
                score += 10
            if query_lower in section_data['description'].lower():
                score += 5
            for keyword in section_data['keywords']:
                if query_lower in keyword.lower():
                    score += 3
                    break
            
            if score > 0:
                results.append({
                    'type': 'section',
                    'title': section_data['title'],
                    'subtitle': 'Section du site',
                    'url': section_data['url'],
                    'score': score,
                    'description': section_data['description']
                })
        
        # === CONTENU DYNAMIQUE DE LA BASE DE DONNÉES ===
        
        # Rechercher dans les événements
        try:
            evenements = Evenement.objects.all()
            for ev in evenements:
                score = 0
                if query_lower in ev.titre.lower():
                    score += 10
                if query_lower in ev.sous_titre.lower():
                    score += 5
                if query_lower in ev.objectifs.lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'type': 'evenement',
                        'title': ev.titre,
                        'subtitle': ev.sous_titre,
                        'url': f'/evenement/{ev.edition}/',
                        'score': score,
                        'description': ev.objectifs[:100] + '...' if len(ev.objectifs) > 100 else ev.objectifs
                    })
        except Exception as e:
            print(f"Error searching events: {e}")
        
        # Rechercher dans les chiffres clés
        try:
            chiffres = ChiffreCle.objects.all()
            for c in chiffres:
                if query_lower in c.label.lower():
                    results.append({
                        'type': 'chiffre',
                        'title': f'{c.nombre}{c.suffixe} {c.label}',
                        'subtitle': f'Chiffre clé - {c.get_edition_display()}',
                        'url': f'/evenement/{c.edition}/',
                        'score': 2,
                        'description': f'Statistique pour {c.get_edition_display()}'
                    })
        except Exception as e:
            print(f"Error searching chiffres: {e}")
        
        # Rechercher dans les partenaires
        try:
            partenaires = Partenaire.objects.all()
            for p in partenaires:
                score = 0
                if query_lower in p.nom.lower():
                    score += 5
                if query_lower in p.description.lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'type': 'partenaire',
                        'title': p.nom,
                        'subtitle': f'Partenaire {p.categorie.title()}',
                        'url': f'/#partenaires',
                        'score': score,
                        'description': p.description[:100] + '...' if len(p.description) > 100 else p.description
                    })
        except Exception as e:
            print(f"Error searching partenaires: {e}")
        
        # Rechercher dans les experts
        try:
            experts = Expert.objects.all()
            for e in experts:
                score = 0
                if query_lower in e.nom.lower():
                    score += 5
                if query_lower in e.bio.lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'type': 'expert',
                        'title': e.nom,
                        'subtitle': f'Expert - {e.titre}',
                        'url': f'/#experts',
                        'score': score,
                        'description': e.bio[:100] + '...' if len(e.bio) > 100 else e.bio
                    })
        except Exception as e:
            print(f"Error searching experts: {e}")
        
        # Rechercher dans la configuration du site
        try:
            config = SiteConfiguration.get()
            config_fields = {
                'hero_titre': config.hero_titre,
                'hero_sous_titre': getattr(config, 'hero_sous_titre', ''),
                'dounia1_defis': config.dounia1_defis,
                'dounia1_opportunites': config.dounia1_opportunites,
                'dounia2_phase1': config.dounia2_phase1,
                'dounia2_phase2': config.dounia2_phase2,
                'dounia2_phase3': config.dounia2_phase3,
                'dounia2_phase4': config.dounia2_phase4,
                'rapport_points': config.rapport_points,
            }
            
            for field_name, field_value in config_fields.items():
                if field_value and query_lower in field_value.lower():
                    results.append({
                        'type': 'page',
                        'title': f'Contenu: {field_name.replace("_", " ").title()}',
                        'subtitle': 'Configuration du site',
                        'url': '/',
                        'score': 2,
                        'description': field_value[:100] + '...' if len(field_value) > 100 else field_value
                    })
        except Exception as e:
            print(f"Error searching config: {e}")
        
        # === RECHERCHE GÉNÉRIQUE - TROUVE N'IMPORTE QUOI ===
        
        # Si aucun résultat trouvé, chercher dans tout le texte possible
        if not results:
            generic_content = [
                {'title': 'DounIA', 'keywords': ['dounia', 'données', 'numériques', 'intelligence', 'artificielle', 'guinée', 'conférence', 'projet'], 'url': '#hero'},
                {'title': 'Inscription', 'keywords': ['inscription', 'formulaire', 'participer', 's\'inscrire', 'inscription'], 'url': '#inscription'},
                {'title': 'Contact', 'keywords': ['contact', 'adresse', 'email', 'téléphone', 'localisation', 'contact'], 'url': '#contact'},
                {'title': 'Événements', 'keywords': ['événements', 'dounia1', 'dounia2', 'conférence', 'événement'], 'url': '#evenements'},
                {'title': 'Partenaires', 'keywords': ['partenaires', 'partenaire', 'collaboration', 'soutien'], 'url': '#partenaires'},
                {'title': 'Experts', 'keywords': ['experts', 'expert', 'intervenant', 'spécialiste', 'conférencier'], 'url': '#experts'},
                {'title': 'Ateliers', 'keywords': ['ateliers', 'atelier', 'formation', 'pratique', 'atelier'], 'url': '#ateliers'},
                {'title': 'Podcast', 'keywords': ['podcast', 'audio', 'discussion', 'entretien', 'podcast'], 'url': '#podcast'},
                {'title': 'Rapport', 'keywords': ['rapport', 'bilan', 'résultats', 'points', 'rapport'], 'url': '#rapport'},
                {'title': 'Admin', 'keywords': ['admin', 'administration', 'gestion', 'admin'], 'url': '/gestion/'},
            ]
            
            for item in generic_content:
                for keyword in item['keywords']:
                    if query_lower in keyword.lower():
                        results.append({
                            'type': 'page',
                            'title': item['title'],
                            'subtitle': 'Page du site',
                            'url': item['url'],
                            'score': 1,
                            'description': f'Page contenant "{keyword}"'
                        })
                        break
        
        # Trier par score
        results.sort(key=lambda x: x['score'], reverse=True)
        print(f"Found {len(results)} results")  # Debug
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        from django.http import JsonResponse
        return JsonResponse({
            'query': query,
            'results': results,
            'count': len(results)
        })
    
    # Return HTML for direct access
    context = {
        'query': query,
        'results': results,
        'count': len(results)
    }
    
    return render(request, 'inscriptions/search_results.html', context)


def event_page(request, event_slug):
    """Page détaillée d'un événement DounIA"""
    from .models import DouniaEvent, EvenementImage
    
    try:
        event = DouniaEvent.objects.get(event_slug=event_slug, actif=True)
    except DouniaEvent.DoesNotExist:
        # Fallback aux anciennes données si le nouveau modèle n'existe pas
        event_data = get_evenement_data(event_slug)
        if not event_data['evenement']:
            raise Http404("Événement non trouvé")
        
        context = {
            'event': event_data['evenement'],
            'objectifs': event_data['objectifs'],
            'images': event_data['images'],
            'chiffres': event_data['chiffres'],
            'event_slug': event_slug,
            'page_title': f"{event_data['evenement'].titre} - DounIA",
            'meta_description': event_data['evenement'].description or f"Découvrez {event_data['evenement'].titre}",
        }
        return render(request, 'inscriptions/event.html', context)
    
    # Utiliser les nouvelles données du modèle DouniaEvent
    hero_images = list(
        EvenementImage.objects.filter(
            evenement=event,
            active=True,
            position='hero',
        ).order_by('ordre', 'date_ajout')
    )
    images = list(
        EvenementImage.objects.filter(
            evenement=event,
            active=True,
            position='galerie',
        ).order_by('ordre', 'date_ajout')
    )
    context = {
        'evenement': event,
        'hero_images': hero_images,
        'images': images,
        'event_slug': event_slug,
        'page_title': event.get_meta_title(),
        'meta_description': event.meta_description or f"Découvrez {event.titre_hero}",
    }
    return render(request, 'inscriptions/event.html', context)


@staff_required
def admin_evenements(request):
    """Gestion des événements (DounIA 1 / DounIA 2)"""
    try:
        _ = Evenement.objects.first()
    except OperationalError:
        messages.error(request, "Tables événements non créées. Exécutez les migrations (python manage.py migrate).")
        return redirect('admin_contenu_page')

    if request.method == 'POST':
        action = request.POST.get('action')
        edition = request.POST.get('edition')

        if action == 'save_evenement' and edition:
            ev, _ = Evenement.objects.get_or_create(edition=edition)
            ev.titre = request.POST.get('titre', ev.titre)
            ev.sous_titre = request.POST.get('sous_titre', ev.sous_titre)
            ev.objectifs = request.POST.get('objectifs', ev.objectifs)
            ev.save()
            messages.success(request, f"Événement {ev.get_edition_display()} mis à jour")
            return redirect('admin_evenements')

        if action == 'add_image' and edition:
            ev, _ = Evenement.objects.get_or_create(edition=edition)
            img = EvenementImage(
                evenement=ev,
                titre=request.POST.get('image_titre', ''),
                image_url=request.POST.get('image_url', ''),
                ordre=int(request.POST.get('ordre', 0)),
                active=True,
            )
            if request.FILES.get('image'):
                img.image = request.FILES['image']
            img.save()
            messages.success(request, 'Image ajoutée')
            return redirect('admin_evenements')

        if action == 'delete_image':
            pk = request.POST.get('pk')
            EvenementImage.objects.filter(pk=pk).delete()
            messages.success(request, 'Image supprimée')
            return redirect('admin_evenements')

    ev1, _ = Evenement.objects.get_or_create(edition='dounia1')
    ev2, _ = Evenement.objects.get_or_create(edition='dounia2')

    context = {
        'ev1': ev1,
        'ev2': ev2,
        'images1': EvenementImage.objects.filter(evenement=ev1).order_by('ordre', 'date_ajout'),
        'images2': EvenementImage.objects.filter(evenement=ev2).order_by('ordre', 'date_ajout'),
    }
    return render(request, 'gestion/evenements.html', context)


def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            inscription = form.save()
            
            # Envoyer l'email de confirmation
            try:
                sujet = f"Nouvelle inscription - {inscription.nom} {inscription.prenom}"
                message = f"""
Nouvelle inscription à DounIA:

Nom: {inscription.nom}
Prénom: {inscription.prenom}
Email: {inscription.email}
WhatsApp: {inscription.whatsapp}
Institution: {inscription.institution}
Fonction: {inscription.fonction}
Profil: {inscription.get_profil_display()}
Atelier: {inscription.get_atelier_display()}
Engagement: {inscription.get_engagement_display()}
Format: {inscription.get_format_preference_display()}
Disponibilité: {inscription.disponibilite}
Motivation: {inscription.motivation}
Consentement RGPD: {inscription.validation_engagement}
Date: {timezone.now().strftime('%d/%m/%Y %H:%M')}
                """
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Envoyer à l'admin
                    fail_silently=True,
                )
            except Exception:
                pass
            
            return redirect('merci')
        context = _landing_context_with_form(form)
        return render(request, 'inscriptions/landing.html', context)

    return redirect('/#inscription')


def merci(request):
    return render(request, 'inscriptions/merci.html')


def rapport_view_pdf(request):
    """Serve PDF inline for viewing only (no download headers)"""
    config = SiteConfiguration.get()
    if config.rapport_fichier:
        import mimetypes
        file_path = config.rapport_fichier.path
        try:
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline'
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
                response['X-Content-Type-Options'] = 'nosniff'
                return response
        except FileNotFoundError:
            return HttpResponse('Fichier non trouvé', status=404)
    return HttpResponse('Aucun fichier configuré', status=404)


def rapport_download(request):
    """Vue pour le téléchargement du rapport PDF"""
    if request.method == 'POST':
        nom = request.POST.get('nom', '')
        prenom = request.POST.get('prenom', '')
        email = request.POST.get('email', '')
        institution = request.POST.get('institution', '')
        
        # Envoyer l'email de notification
        try:
            sujet = f"Téléchargement du rapport - {nom} {prenom}"
            message = f"""
Téléchargement du rapport DounIA:

Nom: {nom}
Prénom: {prenom}
Email: {email}
Institution: {institution}
Date: {timezone.now().strftime('%d/%m/%Y %H:%M')}
            """
            send_mail(
                sujet,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Envoyer à l'admin
                fail_silently=True,
            )
        except Exception:
            pass
        
        # Rediriger vers le fichier uploadé ou le lien externe
        config = SiteConfiguration.get()
        if config.rapport_fichier:
            return redirect(config.rapport_fichier.url)
        elif config.rapport_lien:
            return redirect(config.rapport_lien)
        else:
            messages.error(request, "Le rapport n'est pas encore disponible.")
            return redirect('landing_page')
    
    return redirect('landing_page')


@staff_required
def admin_dashboard(request):
    """Tableau de bord administrateur"""
    total = Inscription.objects.count()

    # Statistiques par atelier
    stats_atelier = []
    ateliers = list(Atelier.objects.filter(active=True).order_by('ordre', 'label'))
    if ateliers:
        for a in ateliers:
            c = Inscription.objects.filter(atelier=a.code).count()
            if c:
                stats_atelier.append({'label': a.label, 'count': c})
    else:
        for val, label in Inscription.ATELIER_CHOICES:
            c = Inscription.objects.filter(atelier=val).count()
            if c:
                stats_atelier.append({'label': label, 'count': c})

    # Statistiques par profil
    stats_profil = []
    for val, label in Inscription.PROFIL_CHOICES:
        c = Inscription.objects.filter(profil=val).count()
        if c:
            stats_profil.append({'label': label, 'count': c})

    # Statistiques par format
    stats_format = []
    for val, label in Inscription.FORMAT_CHOICES:
        c = Inscription.objects.filter(format_preference=val).count()
        if c:
            stats_format.append({'label': label, 'count': c})

    # Statistiques par engagement
    stats_engagement = []
    for val, label in Inscription.ENGAGEMENT_CHOICES:
        c = Inscription.objects.filter(engagement=val).count()
        if c:
            stats_engagement.append({'label': label, 'count': c})

    recent = Inscription.objects.all().order_by('-date_inscription')[:10]

    context = {
        'total': total,
        'stats_atelier': stats_atelier,
        'stats_profil': stats_profil,
        'stats_format': stats_format,
        'stats_engagement': stats_engagement,
        'recent': recent,
    }
    return render(request, 'gestion/dashboard.html', context)


@staff_required
def admin_inscriptions(request):
    """Gestion des inscriptions"""
    inscriptions = Inscription.objects.all().order_by('-date_inscription')

    # Filtres
    q = request.GET.get('q', '')
    current_atelier = request.GET.get('atelier', '')
    current_profil = request.GET.get('profil', '')
    current_format = request.GET.get('format', '')

    if q:
        inscriptions = inscriptions.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) |
            Q(email__icontains=q) | Q(institution__icontains=q)
        )
    if current_atelier:
        inscriptions = inscriptions.filter(atelier=current_atelier)
    if current_profil:
        inscriptions = inscriptions.filter(profil=current_profil)
    if current_format:
        inscriptions = inscriptions.filter(format_preference=current_format)

    context = {
        'inscriptions': inscriptions,
        'total': inscriptions.count(),
        'atelier_choices': Inscription.ATELIER_CHOICES,
        'profil_choices': Inscription.PROFIL_CHOICES,
        'format_choices': Inscription.FORMAT_CHOICES,
        'current_search': q,
        'current_atelier': current_atelier,
        'current_profil': current_profil,
        'current_format': current_format,
    }
    return render(request, 'gestion/inscriptions.html', context)


@staff_required
def admin_inscription_detail(request, pk):
    """Détail d'une inscription"""
    inscription = get_object_or_404(Inscription, pk=pk)
    context = {'inscription': inscription}
    return render(request, 'gestion/detail.html', context)


@staff_required
def admin_inscription_edit(request, pk):
    """Modifier une inscription"""
    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        inscription.nom = request.POST.get('nom', inscription.nom)
        inscription.prenom = request.POST.get('prenom', inscription.prenom)
        inscription.email = request.POST.get('email', inscription.email)
        inscription.whatsapp = request.POST.get('whatsapp', inscription.whatsapp)
        inscription.institution = request.POST.get('institution', inscription.institution)
        inscription.fonction = request.POST.get('fonction', inscription.fonction)
        inscription.profil = request.POST.get('profil', inscription.profil)
        inscription.atelier = request.POST.get('atelier', inscription.atelier)
        inscription.engagement = request.POST.get('engagement', inscription.engagement)
        inscription.format_preference = request.POST.get('format_preference', inscription.format_preference)
        inscription.disponibilite = request.POST.get('disponibilite', inscription.disponibilite)
        inscription.motivation = request.POST.get('motivation', inscription.motivation)
        inscription.save()
        messages.success(request, f'Inscription de {inscription.prenom} {inscription.nom} modifiée avec succès')
        return redirect('admin_inscription_detail', pk=inscription.pk)
    context = {
        'inscription': inscription,
        'atelier_choices': Inscription.ATELIER_CHOICES,
        'profil_choices': Inscription.PROFIL_CHOICES,
        'engagement_choices': Inscription.ENGAGEMENT_CHOICES,
        'format_choices': Inscription.FORMAT_CHOICES,
        'disponibilite_choices': Inscription.DISPONIBILITE_CHOICES,
    }
    return render(request, 'gestion/edit.html', context)


@staff_required
def admin_inscription_delete(request, pk):
    """Supprimer une inscription"""
    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        nom = f"{inscription.prenom} {inscription.nom}"
        inscription.delete()
        messages.success(request, f'Inscription de {nom} supprimée')
        return redirect('admin_inscriptions')
    context = {'inscription': inscription}
    return render(request, 'gestion/delete.html', context)


@staff_required
def admin_inscription_valider(request, pk):
    """Valider une inscription et envoyer l'agenda"""
    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        inscription.valide = True
        inscription.date_validation = timezone.now()
        inscription.save()
        messages.success(request, f'Inscription de {inscription.prenom} {inscription.nom} validée avec succès')
    return redirect('admin_inscription_detail', pk=inscription.pk)


@staff_required
def admin_contenu_page(request):
    """Page de gestion du contenu"""
    config = SiteConfiguration.get()
    context = {
        'config': config,
        'chiffres': ChiffreCle.objects.all().order_by('ordre'),
        'partenaires_list': Partenaire.objects.all().order_by('ordre'),
    }
    return render(request, 'gestion/contenu_page.html', context)


@staff_required
def admin_chiffres(request):
    """Gestion des chiffres clés"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            c = ChiffreCle(
                edition=request.POST.get('edition', 'dounia1'),
                nombre=int(request.POST.get('nombre', 0)),
                suffixe=request.POST.get('suffixe', '+') or '',
                label=request.POST.get('label', ''),
                ordre=int(request.POST.get('ordre', 0)),
            )
            c.save()
            messages.success(request, 'Chiffre ajouté')
            return redirect('admin_chiffres')

        if action == 'edit':
            pk = request.POST.get('pk')
            try:
                c = ChiffreCle.objects.get(pk=pk)
                c.edition = request.POST.get('edition', c.edition)
                c.nombre = int(request.POST.get('nombre', c.nombre))
                c.suffixe = request.POST.get('suffixe', c.suffixe)
                c.label = request.POST.get('label', c.label)
                c.ordre = int(request.POST.get('ordre', c.ordre))
                c.save()
                messages.success(request, 'Chiffre mis à jour')
            except ChiffreCle.DoesNotExist:
                messages.error(request, 'Chiffre introuvable')
            return redirect('admin_chiffres')

        if action == 'delete':
            pk = request.POST.get('pk')
            ChiffreCle.objects.filter(pk=pk).delete()
            messages.success(request, 'Chiffre supprimé')
            return redirect('admin_chiffres')

    chiffres = ChiffreCle.objects.all().order_by('edition', 'ordre')
    context = {
        'chiffres': chiffres,
        'edition_choices': getattr(ChiffreCle, 'EDITION_CHOICES', [('dounia1', 'DounIA 1'), ('dounia2', 'DounIA 2')]),
    }
    return render(request, 'gestion/chiffres.html', context)


@staff_required
def admin_experts(request):
    """Gestion des experts"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            e = Expert(
                nom=request.POST.get('nom', ''),
                specialite=request.POST.get('specialite', ''),
                ordre=int(request.POST.get('ordre', 0)),
            )
            if request.FILES.get('photo'):
                e.photo = request.FILES['photo']
            e.save()
            messages.success(request, 'Expert ajouté avec succès')
            return redirect('admin_experts')

        if action == 'edit':
            pk = request.POST.get('pk')
            try:
                e = Expert.objects.get(pk=pk)
                e.nom = request.POST.get('nom', e.nom)
                e.specialite = request.POST.get('specialite', e.specialite)
                e.ordre = int(request.POST.get('ordre', e.ordre))
                if request.FILES.get('photo'):
                    e.photo = request.FILES['photo']
                e.save()
                messages.success(request, 'Expert mis à jour avec succès')
            except Expert.DoesNotExist:
                messages.error(request, 'Expert introuvable')
            return redirect('admin_experts')

        if action == 'delete':
            pk = request.POST.get('pk')
            Expert.objects.filter(pk=pk).delete()
            messages.success(request, 'Expert supprimé')
            return redirect('admin_experts')

    experts = Expert.objects.all().order_by('ordre')
    context = {
        'experts_list': experts,
    }
    return render(request, 'gestion/experts.html', context)


@staff_required
def admin_partenaires(request):
    """Gestion des partenaires"""
    if request.method == 'POST':
        action = request.POST.get('action')
        ordre_raw = (request.POST.get('ordre') or '').strip()
        try:
            ordre_value = int(ordre_raw) if ordre_raw != '' else 0
        except (TypeError, ValueError):
            ordre_value = 0
        if action == 'add':
            p = Partenaire(
                nom=request.POST.get('nom', ''),
                categorie=request.POST.get('categorie', 'institutionnel'),
                site_web=request.POST.get('site_web', ''),
                ordre=ordre_value,
            )
            if request.FILES.get('logo'):
                p.logo = request.FILES['logo']
            p.save()
            messages.success(request, 'Partenaire ajouté avec succès')
        elif action == 'edit':
            pk = request.POST.get('pk')
            try:
                p = Partenaire.objects.get(pk=pk)
                p.nom = request.POST.get('nom', p.nom)
                p.categorie = request.POST.get('categorie', p.categorie)
                p.site_web = request.POST.get('site_web', p.site_web)
                p.ordre = ordre_value
                if request.FILES.get('logo'):
                    p.logo = request.FILES['logo']
                p.save()
                messages.success(request, 'Partenaire mis à jour avec succès')
            except Partenaire.DoesNotExist:
                messages.error(request, 'Partenaire introuvable')
        elif action == 'delete':
            pk = request.POST.get('pk')
            Partenaire.objects.filter(pk=pk).delete()
            messages.success(request, 'Partenaire supprimé')
        return redirect('admin_partenaires')

    partenaires = Partenaire.objects.all().order_by('ordre')
    context = {
        'partenaires_list': partenaires,
    }
    return render(request, 'gestion/partenaires.html', context)


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


@staff_required
def admin_dounia_events(request):
    """Interface de gestion des événements DounIA"""
    from .models import DouniaEvent
    
    # Récupérer ou créer les événements DounIA 1 et 2
    dounia1, created1 = DouniaEvent.objects.get_or_create(
        event_slug='dounia1',
        defaults={
            'titre_hero': 'DounIA 1 - Lancement',
            'description_hero': 'Premier événement de concertation sur la gouvernance des données et l\'intelligence artificielle en Guinée.',
            'objectifs_description': 'Établir les fondations de la gouvernance des données en Guinée.',
            'objectifs_points': [
                'Partager les connaissances acquises',
                'Présenter les recommandations concrètes',
                'Faciliter la prise de décision'
            ],
            'chiffres': [
                {'nombre': '150+', 'label': 'Participants'},
                {'nombre': '8', 'label': 'Ateliers'},
                {'nombre': '50+', 'label': 'Recommandations'}
            ],
            'programme_description': 'Programme détaillé de la première édition DounIA.',
            'programme_sessions': [
                {'heure': '09:00', 'titre': 'Ouverture', 'description': 'Discours d\'ouverture et présentation'},
                {'heure': '10:00', 'titre': 'Atelier 1', 'description': 'Gouvernance des données'},
                {'heure': '14:00', 'titre': 'Atelier 2', 'description': 'Intelligence artificielle'}
            ],
            'inscription_description': 'Inscrivez-vous pour participer à DounIA 1.',
            'meta_description': 'Premier événement DounIA - Gouvernance des données et IA en Guinée'
        }
    )
    
    dounia2, created2 = DouniaEvent.objects.get_or_create(
        event_slug='dounia2',
        defaults={
            'titre_hero': 'DounIA 2 - Continuité',
            'description_hero': 'Deuxième événement de consolidation des acquis et de planification future.',
            'objectifs_description': 'Consolider les acquis et planifier l\'avenir.',
            'objectifs_points': [
                'Consolider les acquis',
                'Planifier l\'avenir',
                'Mettre en œuvre les recommandations'
            ],
            'chiffres': [
                {'nombre': '200+', 'label': 'Participants attendus'},
                {'nombre': '10', 'label': 'Ateliers prévus'},
                {'nombre': '100+', 'label': 'Actions planifiées'}
            ],
            'programme_description': 'Programme de la deuxième édition DounIA.',
            'programme_sessions': [
                {'heure': '09:00', 'titre': 'État des lieux', 'description': 'Bilan de DounIA 1'},
                {'heure': '11:00', 'titre': 'Ateliers avancés', 'description': 'Approfondissement thématique'},
                {'heure': '15:00', 'titre': 'Plan d\'action', 'description': 'Définition des prochaines étapes'}
            ],
            'inscription_description': 'Inscrivez-vous pour participer à DounIA 2.',
            'meta_description': 'Deuxième événement DounIA - Consolidation et planification'
        }
    )
    
    if request.method == 'POST':
        event_slug = request.POST.get('event_slug')
        
        try:
            event = DouniaEvent.objects.get(event_slug=event_slug)
            
            # Mise à jour des informations hero
            event.titre_hero = request.POST.get('titre_hero', event.titre_hero)
            event.description_hero = request.POST.get('description_hero', event.description_hero)
            event.hero_image_url = request.POST.get('hero_image_url', event.hero_image_url)
            event.bouton_principal_texte = request.POST.get('bouton_principal_texte', event.bouton_principal_texte)
            event.bouton_principal_lien = request.POST.get('bouton_principal_lien', event.bouton_principal_lien)
            event.bouton_secondaire_texte = request.POST.get('bouton_secondaire_texte', event.bouton_secondaire_texte)
            event.bouton_secondaire_lien = request.POST.get('bouton_secondaire_lien', event.bouton_secondaire_lien)

            if 'hero_image' in request.FILES:
                event.hero_image = request.FILES['hero_image']
            
            # Section objectifs
            event.objectifs_titre = request.POST.get('objectifs_titre', event.objectifs_titre)
            event.objectifs_description = request.POST.get('objectifs_description', event.objectifs_description)
            
            # Section programme
            event.programme_titre = request.POST.get('programme_titre', event.programme_titre)
            event.programme_description = request.POST.get('programme_description', event.programme_description)
            
            # Section partenaires
            event.partenaires_titre = request.POST.get('partenaires_titre', event.partenaires_titre)
            event.partenaires_description = request.POST.get('partenaires_description', event.partenaires_description)
            
            # Section inscription
            event.inscription_titre = request.POST.get('inscription_titre', event.inscription_titre)
            event.inscription_description = request.POST.get('inscription_description', event.inscription_description)
            event.inscription_lieu = request.POST.get('inscription_lieu', event.inscription_lieu)
            
            # Section contact
            event.contact_titre = request.POST.get('contact_titre', event.contact_titre)
            event.contact_email = request.POST.get('contact_email', event.contact_email)
            event.contact_telephone = request.POST.get('contact_telephone', event.contact_telephone)
            event.contact_adresse = request.POST.get('contact_adresse', event.contact_adresse)
            
            # SEO
            event.meta_title = request.POST.get('meta_title', event.meta_title)
            event.meta_description = request.POST.get('meta_description', event.meta_description)
            
            # Gestion des listes JSON
            objectifs_points = request.POST.getlist('objectifs_points')
            event.objectifs_points = [point for point in objectifs_points if point.strip()]
            
            # Gestion des chiffres
            event.chiffres_image_url = request.POST.get('chiffres_image_url', event.chiffres_image_url)
            if 'chiffres_image' in request.FILES:
                event.chiffres_image = request.FILES['chiffres_image']

            chiffres_nombres = request.POST.getlist('chiffres_nombre')
            chiffres_labels = request.POST.getlist('chiffres_label')
            
            chiffres = []
            for i in range(len(chiffres_nombres)):
                if chiffres_nombres[i].strip() or chiffres_labels[i].strip():
                    chiffres.append({
                        'nombre': chiffres_nombres[i],
                        'label': chiffres_labels[i]
                    })
            event.chiffres = chiffres
            
            # Gestion des sessions
            sessions_heures = request.POST.getlist('session_heure')
            sessions_titres = request.POST.getlist('session_titre')
            sessions_descriptions = request.POST.getlist('session_description')
            
            sessions = []
            for i in range(len(sessions_heures)):
                if sessions_heures[i].strip() or sessions_titres[i].strip():
                    sessions.append({
                        'heure': sessions_heures[i],
                        'titre': sessions_titres[i],
                        'description': sessions_descriptions[i]
                    })
            event.programme_sessions = sessions
            
            # Gestion de la date limite
            date_limite_str = request.POST.get('inscription_date_limite', '')
            if date_limite_str:
                from datetime import datetime
                try:
                    event.inscription_date_limite = datetime.strptime(date_limite_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            event.actif = request.POST.get('actif') == 'on'
            event.save()
            
            messages.success(request, f'L\'événement {event.get_event_slug_display()} a été mis à jour avec succès.')
            return redirect('admin_dounia_events')
            
        except DouniaEvent.DoesNotExist:
            messages.error(request, 'Événement non trouvé.')
    
    context = {
        'dounia1': dounia1,
        'dounia2': dounia2,
        'page_title': 'Gestion Événements DounIA',
    }
    return render(request, 'gestion/admin_dounia_events.html', context)


@staff_required
def admin_restitution(request):
    """Interface de gestion de la page restitution"""
    from .models import Restitution
    
    # Récupérer ou créer l'instance de restitution
    restitution, created = Restitution.objects.get_or_create(
        pk=1,
        defaults={
            'mission_points': [
                'Partager les connaissances acquises',
                'Présenter les recommandations concrètes',
                'Faciliter la prise de décision'
            ],
            'public_points': [
                'Décideurs politiques',
                'Experts techniques',
                'Société civile',
                'Secteur privé'
            ],
            'chronologie': [
                {
                    'date': 'Janvier 2024',
                    'titre': 'Lancement de DounIA 1',
                    'description': 'Démarrage du processus de concertation et des premiers ateliers thématiques.'
                },
                {
                    'date': 'Février - Mars 2024',
                    'titre': 'Ateliers Thématiques',
                    'description': 'Réalisation de 8 ateliers sectoriels avec plus de 150 participants.'
                },
                {
                    'date': 'Avril 2024',
                    'titre': 'Analyse et Synthèse',
                    'description': 'Compilation des résultats et élaboration des recommandations stratégiques.'
                },
                {
                    'date': 'Mai 2024',
                    'titre': 'Restitution Officielle',
                    'description': 'Présentation des résultats et lancement de DounIA 2.'
                }
            ]
        }
    )
    
    if request.method == 'POST':
        # Mise à jour des informations hero
        restitution.titre_hero = request.POST.get('titre_hero', restitution.titre_hero)
        restitution.description_hero = request.POST.get('description_hero', restitution.description_hero)
        restitution.hero_image_url = request.POST.get('hero_image_url', restitution.hero_image_url)

        if 'hero_image' in request.FILES:
            restitution.hero_image = request.FILES['hero_image']
        
        # Section objectifs
        restitution.mission_titre = request.POST.get('mission_titre', restitution.mission_titre)
        restitution.mission_description = request.POST.get('mission_description', restitution.mission_description)
        restitution.public_titre = request.POST.get('public_titre', restitution.public_titre)
        restitution.public_description = request.POST.get('public_description', restitution.public_description)
        
        # Section chiffres clés
        restitution.participants_nombre = request.POST.get('participants_nombre', restitution.participants_nombre)
        restitution.participants_label = request.POST.get('participants_label', restitution.participants_label)
        restitution.ateliers_nombre = request.POST.get('ateliers_nombre', restitution.ateliers_nombre)
        restitution.ateliers_label = request.POST.get('ateliers_label', restitution.ateliers_label)
        restitution.recommandations_nombre = request.POST.get('recommandations_nombre', restitution.recommandations_nombre)
        restitution.recommandations_label = request.POST.get('recommandations_label', restitution.recommandations_label)
        restitution.duree_nombre = request.POST.get('duree_nombre', restitution.duree_nombre)
        restitution.duree_label = request.POST.get('duree_label', restitution.duree_label)
        
        # Section rapports
        restitution.rapport_synthese_titre = request.POST.get('rapport_synthese_titre', restitution.rapport_synthese_titre)
        restitution.rapport_synthese_description = request.POST.get('rapport_synthese_description', restitution.rapport_synthese_description)
        restitution.rapport_detail_titre = request.POST.get('rapport_detail_titre', restitution.rapport_detail_titre)
        restitution.rapport_detail_description = request.POST.get('rapport_detail_description', restitution.rapport_detail_description)
        
        # Section call-to-action
        restitution.cta_titre = request.POST.get('cta_titre', restitution.cta_titre)
        restitution.cta_description = request.POST.get('cta_description', restitution.cta_description)
        
        # Gestion des fichiers
        if 'rapport_synthese_fichier' in request.FILES:
            restitution.rapport_synthese_fichier = request.FILES['rapport_synthese_fichier']
        if 'rapport_detail_fichier' in request.FILES:
            restitution.rapport_detail_fichier = request.FILES['rapport_detail_fichier']
        
        # Gestion des listes JSON
        mission_points = request.POST.getlist('mission_points')
        public_points = request.POST.getlist('public_points')
        
        # Nettoyer les listes (enlever les vides)
        restitution.mission_points = [point for point in mission_points if point.strip()]
        restitution.public_points = [point for point in public_points if point.strip()]
        
        # Gestion de la chronologie
        chronologie_dates = request.POST.getlist('chronologie_date')
        chronologie_titres = request.POST.getlist('chronologie_titre')
        chronologie_descriptions = request.POST.getlist('chronologie_description')
        
        chronologie = []
        for i in range(len(chronologie_dates)):
            if chronologie_dates[i].strip() or chronologie_titres[i].strip():
                chronologie.append({
                    'date': chronologie_dates[i],
                    'titre': chronologie_titres[i],
                    'description': chronologie_descriptions[i]
                })
        restitution.chronologie = chronologie
        
        restitution.save()
        messages.success(request, 'Les informations de restitution ont été mises à jour avec succès.')
        return redirect('admin_restitution')
    
    context = {
        'restitution': restitution,
        'page_title': 'Gestion Restitution',
    }
    return render(request, 'gestion/admin_restitution.html', context)


@staff_required
def admin_ateliers(request):
    """Gestion des ateliers"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            code = (request.POST.get('code') or '').strip()
            label = (request.POST.get('label') or '').strip()
            description = (request.POST.get('description') or '').strip()
            image_url = (request.POST.get('image_url') or '').strip()
            ordre = int(request.POST.get('ordre') or 0)
            active = request.POST.get('active') == 'on'

            if not code or not label:
                messages.error(request, "Code et libellé sont obligatoires")
                return redirect('admin_ateliers')

            try:
                a = Atelier.objects.create(code=code, label=label, description=description, ordre=ordre, active=active, image_url=image_url)
                
                # Gérer l'upload de l'image
                if 'image' in request.FILES:
                    uploaded_file = request.FILES['image']
                    # Vérifier la taille du fichier (max 5MB)
                    if uploaded_file.size > 5 * 1024 * 1024:
                        messages.error(request, "L'image est trop grande (max 5MB)")
                        a.delete()  # Supprimer l'atelier créé si l'image est trop grande
                    else:
                        try:
                            a.image = uploaded_file
                            a.save()
                            messages.success(request, 'Atelier ajouté avec image')
                        except Exception as e:
                            messages.error(request, f"Erreur lors de l'upload de l'image: {str(e)}")
                            a.save()  # Sauvegarder quand même sans l'image
                else:
                    messages.success(request, 'Atelier ajouté avec succès')
                    
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
            return redirect('admin_ateliers')

        if action == 'edit':
            pk = request.POST.get('pk')
            try:
                a = Atelier.objects.get(pk=pk)
                a.code = (request.POST.get('code') or '').strip()
                a.label = (request.POST.get('label') or '').strip()
                a.description = (request.POST.get('description') or '').strip()
                a.image_url = (request.POST.get('image_url') or '').strip()
                a.ordre = int(request.POST.get('ordre') or 0)
                a.active = request.POST.get('active') == 'on'
                
                if not a.code or not a.label:
                    messages.error(request, "Code et libellé sont obligatoires")
                else:
                    # Gérer l'upload de l'image
                    if 'image' in request.FILES:
                        uploaded_file = request.FILES['image']
                        # Vérifier la taille du fichier (max 5MB)
                        if uploaded_file.size > 5 * 1024 * 1024:
                            messages.error(request, "L'image est trop grande (max 5MB)")
                        else:
                            try:
                                a.image = uploaded_file
                                messages.success(request, "Image uploadée avec succès")
                            except Exception as e:
                                messages.error(request, f"Erreur lors de l'upload de l'image: {str(e)}")
                    
                    a.save()
                    if not messages.get_messages(request):
                        messages.success(request, 'Atelier mis à jour avec succès')
            except Atelier.DoesNotExist:
                messages.error(request, 'Atelier introuvable')
            except Exception as e:
                messages.error(request, f'Erreur technique: {str(e)}')
            return redirect('admin_ateliers')

        if action == 'delete':
            pk = request.POST.get('pk')
            Atelier.objects.filter(pk=pk).delete()
            messages.success(request, 'Atelier supprimé')
            return redirect('admin_ateliers')

    ateliers = Atelier.objects.all().order_by('ordre', 'label')
    context = {
        'ateliers': ateliers,
    }
    return render(request, 'gestion/ateliers.html', context)


@staff_required
def admin_edit_section(request, section):
    """Édition d'une section spécifique"""
    config = SiteConfiguration.get()

    # Define fields_data for each section
    SECTION_DEFS = {
        'hero': {
            'titre': 'Hero',
            'fields': [
                {'name': 'hero_badge', 'label': 'Badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'hero_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'hero_titre_span', 'label': 'Titre (partie en surbrillance)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'hero_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'hero_btn1_texte', 'label': 'Bouton 1 — Texte', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'hero_btn1_lien', 'label': 'Bouton 1 — Lien', 'is_textarea': False, 'is_url': True, 'is_image': False},
                {'name': 'hero_btn2_texte', 'label': 'Bouton 2 — Texte', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'hero_btn2_lien', 'label': 'Bouton 2 — Lien', 'is_textarea': False, 'is_url': True, 'is_image': False},
            ],
        },
        'about': {
            'titre': 'À propos',
            'fields': [
                {'name': 'about_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'about_card1_icone', 'label': 'Carte 1 — Icône (Bootstrap Icons)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card1_titre', 'label': 'Carte 1 — Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card1_texte', 'label': 'Carte 1 — Texte', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'about_card2_icone', 'label': 'Carte 2 — Icône (Bootstrap Icons)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card2_titre', 'label': 'Carte 2 — Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card2_texte', 'label': 'Carte 2 — Texte', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'about_card3_icone', 'label': 'Carte 3 — Icône (Bootstrap Icons)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card3_titre', 'label': 'Carte 3 — Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_card3_texte', 'label': 'Carte 3 — Texte', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },
        'dounia1': {
            'titre': 'DounIA 1',
            'fields': [
                {'name': 'dounia1_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'dounia1_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'dounia1_defis', 'label': 'Défis (un par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Un défi par ligne'},
                {'name': 'dounia1_opportunites', 'label': 'Opportunités (une par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Une opportunité par ligne'},
            ],
        },
        'rapport': {
            'titre': 'Rapport DounIA 1',
            'fields': [
                {'name': 'rapport_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'rapport_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'rapport_description', 'label': 'Description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'rapport_points', 'label': 'Points clés (un par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Un point par ligne'},
                {'name': 'rapport_lien', 'label': 'Lien externe du rapport (optionnel)', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'URL vers le PDF si hébergé ailleurs (Google Drive, etc.). Laissez vide si vous uploadez le fichier ci-dessous.'},
                {'name': 'rapport_fichier', 'label': 'Uploader le PDF du rapport', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': True, 'help_text': 'Uploadez directement le fichier PDF. Ce fichier sera prioritaire sur le lien externe.'},
                {'name': 'rapport_image', 'label': 'Image de couverture du rapport', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée à gauche du rapport sur la page d\'accueil.'},
            ],
        },

        'evenements': {
            'titre': 'Événements (section landing)',
            'fields': [
                {'name': 'evenements_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'evenements_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },
        'podcast': {
            'titre': 'Podcast',
            'fields': [
                {'name': 'podcast_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'podcast_description', 'label': 'Description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'podcast_lien', 'label': 'Lien du podcast', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'URL vers le podcast (Spotify, YouTube, etc.)'},
                {'name': 'podcast_fichier', 'label': 'Fichier audio (optionnel)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': True, 'help_text': 'Uploadez un fichier audio (MP3/WAV). Ce fichier sera prioritaire sur le lien externe.'},
            ],
        },
        'dounia2': {
            'titre': 'DounIA 2',
            'fields': [
                {'name': 'dounia2_badge', 'label': 'Badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'dounia2_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'dounia2_description', 'label': 'Description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'dounia2_phase1', 'label': 'Phase 1 (titre|description)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Format: Titre|Description'},
                {'name': 'dounia2_phase2', 'label': 'Phase 2 (titre|description)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Format: Titre|Description'},
                {'name': 'dounia2_phase3', 'label': 'Phase 3 (titre|description)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Format: Titre|Description'},
                {'name': 'dounia2_phase4', 'label': 'Phase 4 (titre|description)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Format: Titre|Description'},
            ],
        },

        'experts_section': {
            'titre': 'Experts (section landing)',
            'fields': [
                {'name': 'experts_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'experts_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },

        'ateliers_section': {
            'titre': 'Ateliers (section landing)',
            'fields': [
                {'name': 'ateliers_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'ateliers_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },

        'calendrier_section': {
            'titre': 'Calendrier (section landing)',
            'fields': [
                {'name': 'calendrier_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'calendrier_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'calendrier_bg_education', 'label': 'Background — Éducation', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'calendrier_bg_sante', 'label': 'Background — Santé', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'calendrier_bg_justice', 'label': 'Background — Justice', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'calendrier_bg_rh', 'label': 'Background — RH', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'calendrier_bg_finance', 'label': 'Background — Finance', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'calendrier_bg_mines', 'label': 'Background — Mines', 'is_textarea': False, 'is_url': False, 'is_image': True},
            ],
        },
        'video': {
            'titre': 'Section Vidéo',
            'fields': [
                {'name': 'video_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'video_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'video_lien', 'label': 'Lien YouTube / Vimeo (optionnel)', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'Collez un lien YouTube ou Vimeo. Laissez vide si vous uploadez un fichier ci-dessous.'},
                {'name': 'video_fichier', 'label': 'Fichier vidéo MP4 (optionnel)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': True, 'help_text': 'Uploadez un fichier MP4. Ce fichier sera prioritaire sur le lien YouTube.'},
            ],
        },
        'inscription_section': {
            'titre': 'Section Inscription',
            'fields': [
                {'name': 'inscription_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'inscription_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },
        'porteurs': {
            'titre': 'Porteurs du processus',
            'fields': [
                {'name': 'porteur1_nom', 'label': 'Porteur 1 — Nom', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'porteur1_description', 'label': 'Porteur 1 — Description', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'porteur1_logo', 'label': 'Porteur 1 — Logo', 'is_textarea': False, 'is_url': False, 'is_image': True, 'is_file': False, 'help_text': 'Uploadez le logo du porteur 1'},
                {'name': 'porteur2_nom', 'label': 'Porteur 2 — Nom', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'porteur2_description', 'label': 'Porteur 2 — Description', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'porteur2_logo', 'label': 'Porteur 2 — Logo', 'is_textarea': False, 'is_url': False, 'is_image': True, 'is_file': False, 'help_text': 'Uploadez le logo du porteur 2'},
            ],
        },
        'footer': {
            'titre': 'Footer',
            'fields': [
                {'name': 'footer_description', 'label': 'Description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'footer_email', 'label': 'Email de contact', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'footer_lieu', 'label': 'Lieu', 'is_textarea': False, 'is_url': False, 'is_image': False},
            ],
        },
    }

    section_def = SECTION_DEFS.get(section)
    if not section_def:
        messages.error(request, f'Section "{section}" inconnue.')
        return redirect('admin_contenu_page')

    if request.method == 'POST':
        for field in section_def['fields']:
            name = field['name']
            if field.get('is_file') or field.get('is_image'):
                uploaded = request.FILES.get(name)
                if uploaded:
                    setattr(config, name, uploaded)
            else:
                value = request.POST.get(name, '')
                setattr(config, name, value)
        config.save()
        messages.success(request, f'Section "{section_def["titre"]}" mise à jour avec succès')
        return redirect('admin_contenu_page')

    # Build fields_data with current values
    fields_data = []
    for field in section_def['fields']:
        fd = dict(field)
        fd['value'] = getattr(config, field['name'], '')
        if 'help_text' not in fd:
            fd['help_text'] = ''
        fields_data.append(fd)

    context = {
        'config': config,
        'section': section,
        'section_titre': section_def['titre'],
        'fields_data': fields_data,
    }
    return render(request, 'gestion/edit_section.html', context)


@staff_required
def export_inscriptions_csv(request):
    """Export des inscriptions en CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inscriptions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Email', 'Institution', 'Fonction', 'Profil', 'Atelier', 'Date'])
    
    for inscription in Inscription.objects.all().order_by('-date_inscription'):
        writer.writerow([
            inscription.nom,
            inscription.prenom,
            inscription.email,
            inscription.institution,
            inscription.fonction,
            inscription.get_profil_display(),
            inscription.get_atelier_display(),
            inscription.date_inscription.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response


@staff_required
def export_inscriptions_pdf(request):
    """Export des inscriptions en PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus.doctable import TableStyle, Table
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    # Créer le PDF
    doc = SimpleDocTemplate(filename="inscriptions.pdf", pagesize=letter)
    elements = []
    
    # En-tête
    elements.append(Paragraph("Liste des inscriptions DounIA", style=styles['title']))
    elements.append(Spacer(1, 12))
    
    # Tableau des inscriptions
    data = []
    for inscription in Inscription.objects.all().order_by('-date_inscription'):
        data.append([
            inscription.nom,
            inscription.prenom,
            inscription.email,
            inscription.institution,
            inscription.fonction,
            inscription.get_profil_display(),
            inscription.get_atelier_display(),
            inscription.date_inscription.strftime('%d/%m/%Y')
        ])
    
    table = Table(data, style=TableStyle([
        ('BACKGROUNDCOLOR', (0, 51, 102)),
        ('TEXTCOLOR', (255, 255, 255)),
        ('ALIGN', (0, 0, 0)),
        ('FONTNAME', 'Helvetica-Bold'),
        ('FONTSIZE', 10),
        ('GRID', (0, 0, 0, -1, -1, -1, -1, -1)),
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    return doc


@staff_required
def generer_agenda_pdf_view(request):
    """Générer le PDF de l'agenda"""
    return generer_agenda_pdf(request)


@staff_required
def manage_hero_images(request):
    """Vue pour gérer les images du carousel hero (ancienne fonction)"""
    hero_images = HeroCarouselImage.objects.all().order_by('ordre', 'date_ajout')
    
    context = {
        'hero_images': hero_images,
    }
    return render(request, 'inscriptions/manage_hero_images.html', context)


@require_POST
@staff_required
def add_carousel_image(request):
    """Ajouter une image au carousel hero"""
    titre = request.POST.get('titre', '')
    image_url = request.POST.get('image_url', '')
    ordre = int(request.POST.get('ordre', 0))

    if not titre:
        messages.error(request, 'Le titre est obligatoire')
        return redirect('manage_hero_stats_images')

    image_obj = HeroCarouselImage.objects.create(
        titre=titre,
        image_url=image_url,
        ordre=ordre
    )

    if 'image' in request.FILES:
        image_obj.image = request.FILES['image']
        image_obj.save()

    messages.success(request, f'Image carousel "{titre}" ajoutée avec succès')
    return redirect('manage_hero_stats_images')


@require_POST
@staff_required
def toggle_carousel_image(request, image_id):
    """Activer/désactiver une image carousel"""
    image = get_object_or_404(HeroCarouselImage, id=image_id)
    image.active = not image.active
    image.save()
    status = "activée" if image.active else "désactivée"
    return JsonResponse({'success': True, 'status': status})


@require_POST
@staff_required
def delete_carousel_image(request, image_id):
    """Supprimer une image carousel"""
    image = get_object_or_404(HeroCarouselImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


@require_POST
@staff_required
def update_image_order(request):
    """Mettre à jour l'ordre des images (ancienne fonction)"""
    orders = request.POST.getlist('orders[]')
    for i, image_id in enumerate(orders):
        try:
            image = HeroCarouselImage.objects.get(id=image_id)
            image.ordre = i
            image.save()
        except HeroCarouselImage.DoesNotExist:
            continue
    return JsonResponse({'success': True})
