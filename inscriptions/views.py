from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.db.models import Count, Q
from django.db.utils import OperationalError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .forms import InscriptionForm, InscriptionConferenceForm
from .models import Atelier, Inscription, SiteConfiguration, ChiffreCle, Expert, Partenaire, HeroCarouselImage, HeroImage, StatsImage, Evenement, EvenementImage, Avis, Rubrique, Article, InscriptionConference, BadgeTemplate
import csv
from collections import OrderedDict
from django.utils import timezone
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.core.mail import EmailMessage
from .pdf_agenda import generer_agenda_pdf


def is_staff_user(user):
    return user.is_staff


def staff_login_url(request):
    return f"/gestion/login/?next={request.path}"


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or '/gestion/'
            return redirect(next_url)

        messages.error(request, 'Identifiants invalides ou accès non autorisé.')

    return render(request, 'gestion/login.html')


def staff_required(view_func):
    """Require an authenticated staff user for custom gestion views."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect(staff_login_url(request))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@staff_required
def admin_logout(request):
    """Déconnexion de l'admin"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('admin_login')


def atelier_detail(request, atelier_id):
    """Vue pour afficher les détails d'un atelier"""
    atelier = get_object_or_404(Atelier, id=atelier_id, active=True)
    
    context = {
        'page_title': f'{atelier.label} — DounIA',
        'meta_description': atelier.description[:200] if atelier.description else f'Découvrez l\'atelier {atelier.label} de la conférence DounIA',
        'atelier': atelier,
    }
    return render(request, 'inscriptions/atelier_detail.html', context)


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
def toggle_config_field(request, field_name):
    """Basculer un champ booléen de SiteConfiguration (splash_actif, countdown_actif…)"""
    ALLOWED_FIELDS = {'splash_actif', 'countdown_actif'}
    if field_name not in ALLOWED_FIELDS:
        return JsonResponse({'success': False, 'error': 'Champ non autorisé'}, status=403)
    config = SiteConfiguration.get()
    current = getattr(config, field_name, False)
    setattr(config, field_name, not current)
    config.save()
    return JsonResponse({'success': True, 'active': not current})


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
        try:
            from .models import DouniaEvent
            dounia_ev = DouniaEvent.objects.filter(event_slug=edition).first()
            if dounia_ev:
                images = list(EvenementImage.objects.filter(evenement=dounia_ev, active=True).order_by('ordre', 'date_ajout'))
        except (OperationalError, ValueError, Exception):
            images = []
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
    
    restitution, _created = Restitution.objects.get_or_create(
        pk=1,
        defaults={
            'contexte_points': [
                'Partager les principaux enseignements du rapport,',
                'Informer les parties prenantes des suites du processus,',
                'Procéder à la signature collective du Manifeste de Conkary sur les Données Numériques et IA',
                'Et effectuer le lancement sollenel de la plateforme www.dounia.org, l’arrive de DounIA 2, ainsi que la tenue d’ateliers thématiques préparatoires autour des six axes prioritaires.',
            ],
            'objectifs_specifiques': [
                'Présenter officiellement le rapport de synthèse de DounIA 1 ;',
                'Valoriser la démarche scientifique, collaborative et multi-acteurs portée par DounIA ;',
                'Annoncer les six (6) thématiques prioritaires alignées aux piliers stratégiques du programme de Simandou 2040 pour la suite du processus ;',
                'Présenter le calendrier et les modalités d’organisation des ateliers thématiques à venir;', 
                'Annoncer officiellement la tenue de DounIA 2 en octobre 2026 ;',
                'Informer et mobiliser les institutions, la communauté scientifique, les partenaires et les médias.',
            ],
            'resultats_attendus': [
                'Le rapport final de DounIA 1 est officiellement restitué et mis à disposition du public ;',
                'Les six thématiques et le cadre des ateliers préparatoires sont clairement présentés ;',
                'La date et les orientations générales de DounIA 2 sont officiellement annoncées ;',
                'Une couverture médiatique nationale est assurée ;',
                'Les parties prenantes clés sont engagées dans la dynamique de préparation de DounIA 2.',
            ],
            'public_cible': [
                'Secteur Public : Ministères clés, Conseil Nationale de la Transition, autorités de régulation, agences techniques nationales.',
                'Secteur Privé : Entreprises technologiques (locales et internationales), opérateurs télécoms, startups, PME innovantes, incubateurs, accélérateurs.',
                'Monde Académique et Recherche : Universités, centres de recherche, chercheurs, enseignants-chercheurs, experts en IA et sciences des données, étudiants (notamment en Master et Doctorat).',
                "Professionnels Sectoriels : Acteurs de la santé, de l'éducation, de l'agriculture, de la finance, des mines, de l'environnement, de la culture, etc., intéressés par l'application de l'IA.",
                "Société Civile : Organisations œuvrant pour l'inclusion numérique, la protection des données, l'éthique, la vulgarisation scientifique et la participation citoyenne.",
                "Médias et Créateurs : Journalistes, médias spécialisés, créateurs de contenu, artistes et designers explorant les usages et impacts de l'IA.",
                'Partenaires Techniques et Financiers : Organisations internationales, bailleurs de fonds intéressés par le développement numérique et l\'innovation en Guinée.',
            ],
        },
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
        from .models import RestitutionImage
        galerie_images = list(RestitutionImage.objects.filter(active=True, position='galerie').order_by('ordre', 'date_ajout'))
    except Exception:
        galerie_images = []

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

    # Récupérer les articles épinglés pour la page d'accueil
    try:
        articles_epingles = Article.objects.filter(
            statut='publie', visibilite='public', epingle=True, date_publication__lte=timezone.now()
        ).select_related('rubrique')[:3]
    except Exception:
        articles_epingles = []

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
        'galerie_images': galerie_images,
        'articles_epingles': articles_epingles,
        'articles_lies': _articles_pour_emplacement('afficher_accueil'),
    }
    return render(request, 'inscriptions/landing.html', context)


def about_page(request):
    config = SiteConfiguration.get()
    try:
        chiffres = list(ChiffreCle.objects.all().order_by('ordre'))
    except OperationalError:
        chiffres = []
    try:
        experts = Expert.objects.all().order_by('ordre')
    except OperationalError:
        experts = []
    return render(request, 'inscriptions/about.html', {
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'articles_lies': _articles_pour_emplacement('afficher_apropos'),
    })


def _articles_pour_emplacement(champ, limite=6):
    """Retourne les articles publiés cochés pour un emplacement donné du site.

    `champ` est le nom du booléen sur le modèle Article
    (ex: 'afficher_ateliers', 'afficher_evenements', ...).
    """
    try:
        return list(
            Article.objects.filter(
                statut='publie', visibilite='public',
                date_publication__lte=timezone.now(), **{champ: True}
            ).select_related('rubrique')[:limite]
        )
    except Exception:
        return []


def ateliers_page(request):
    config = SiteConfiguration.get()
    try:
        ateliers_db = Atelier.objects.filter(active=True).order_by('ordre')
    except OperationalError:
        ateliers_db = []
    return render(request, 'inscriptions/ateliers.html', {
        'config': config,
        'ateliers_db': ateliers_db,
        'articles_lies': _articles_pour_emplacement('afficher_ateliers'),
    })


def evenements_page(request):
    config = SiteConfiguration.get()
    from .models import DouniaEvent, Restitution
    try:
        dounia1_event = DouniaEvent.objects.get(event_slug='dounia1')
    except DouniaEvent.DoesNotExist:
        dounia1_event = None
    try:
        dounia2_event = DouniaEvent.objects.get(event_slug='dounia2')
    except DouniaEvent.DoesNotExist:
        dounia2_event = None
    try:
        restitution_data = Restitution.objects.get(pk=1)
    except Restitution.DoesNotExist:
        restitution_data = None
    return render(request, 'inscriptions/evenements.html', {
        'config': config,
        'dounia1_event': dounia1_event,
        'dounia2_event': dounia2_event,
        'restitution_data': restitution_data,
        'articles_lies': _articles_pour_emplacement('afficher_evenements'),
    })


def podcast_page(request):
    config = SiteConfiguration.get()
    return render(request, 'inscriptions/podcast.html', {
        'config': config,
        'articles_lies': _articles_pour_emplacement('afficher_podcast'),
    })


def rejoindre_page(request):
    config = SiteConfiguration.get()
    return render(request, 'inscriptions/rejoindre.html', {
        'config': config,
    })


def livrable_page(request):
    config = SiteConfiguration.get()
    rapport_points = [p.strip() for p in config.rapport_points.split('\n') if p.strip()]
    return render(request, 'inscriptions/livrable.html', {
        'config': config,
        'rapport_points': rapport_points,
        'articles_lies': _articles_pour_emplacement('afficher_livrables'),
    })


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

    try:
        ateliers_db = Atelier.objects.filter(active=True).order_by('ordre')
        atelier_map = {a.code: {'label': a.label, 'image': a.get_image_url(), 'description': a.description} for a in ateliers_db}
    except OperationalError:
        atelier_map = {}

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
    # Experts pour la page DounIA 1
    from .models import Expert
    experts = Expert.objects.all().order_by('ordre')

    # Fallback galerie : si aucune image galerie spécifique à l'événement, utiliser les RestitutionImage
    if not images:
        try:
            from .models import RestitutionImage
            images = list(
                RestitutionImage.objects.filter(active=True, position='galerie').order_by('ordre', 'date_ajout')
            )
        except Exception:
            images = []

    context = {
        'evenement': event,
        'hero_images': hero_images,
        'images': images,
        'experts': experts,
        'event_slug': event_slug,
        'page_title': event.get_meta_title(),
        'meta_description': event.meta_description or f"Découvrez {event.titre_hero}",
    }
    template = 'inscriptions/event_dounia2.html' if event_slug == 'dounia2' else 'inscriptions/event.html'
    return render(request, template, context)


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
Source: {inscription.get_source_connaissance_display()}
N° courrier: {inscription.source_connaissance_courrier_numero}
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
        
        # Rediriger vers le lien externe en priorité, sinon le fichier uploadé
        config = SiteConfiguration.get()
        if config.rapport_lien:
            return redirect(config.rapport_lien)
        elif config.rapport_fichier:
            return redirect(config.rapport_fichier.url)
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
            event.hero_video_url = request.POST.get('hero_video_url', event.hero_video_url)
            event.hero_image_url = request.POST.get('hero_image_url', event.hero_image_url)
            event.bouton_principal_texte = request.POST.get('bouton_principal_texte', event.bouton_principal_texte)
            event.bouton_principal_lien = request.POST.get('bouton_principal_lien', event.bouton_principal_lien)
            event.bouton_secondaire_texte = request.POST.get('bouton_secondaire_texte', event.bouton_secondaire_texte)
            event.bouton_secondaire_lien = request.POST.get('bouton_secondaire_lien', event.bouton_secondaire_lien)

            if 'hero_image' in request.FILES:
                event.hero_image = request.FILES['hero_image']
            if 'hero_video' in request.FILES:
                event.hero_video = request.FILES['hero_video']
            
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
            
            # Gestion de la date de lancement (compte à rebours)
            date_lancement_str = request.POST.get('date_lancement', '')
            if date_lancement_str:
                from datetime import datetime
                try:
                    event.date_lancement = datetime.strptime(date_lancement_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass
            elif 'date_lancement' in request.POST:
                event.date_lancement = None
            
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
    from .models import Restitution, RestitutionImage
    
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
        restitution.hero_badge_text = request.POST.get('hero_badge_text', restitution.hero_badge_text)
        restitution.hero_btn1_texte = request.POST.get('hero_btn1_texte', restitution.hero_btn1_texte)
        restitution.hero_btn1_lien = request.POST.get('hero_btn1_lien', restitution.hero_btn1_lien)
        restitution.hero_btn2_texte = request.POST.get('hero_btn2_texte', restitution.hero_btn2_texte)
        restitution.hero_btn2_lien = request.POST.get('hero_btn2_lien', restitution.hero_btn2_lien)
        restitution.hero_image_url = request.POST.get('hero_image_url', restitution.hero_image_url)

        # Countdown date
        countdown_raw = request.POST.get('countdown_date', '').strip()
        if countdown_raw:
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(countdown_raw)
            if parsed:
                restitution.countdown_date = parsed
        else:
            restitution.countdown_date = None

        restitution.section_titre = request.POST.get('section_titre', restitution.section_titre)
        restitution.galerie_titre = request.POST.get('galerie_titre', restitution.galerie_titre)

        if 'hero_image' in request.FILES:
            restitution.hero_image = request.FILES['hero_image']
        
        # TDR PDF upload
        if 'tdr_pdf' in request.FILES:
            restitution.tdr_pdf = request.FILES['tdr_pdf']

        # Section cérémonie (Contexte / Objectif / Résultats / Public)
        restitution.contexte_titre = request.POST.get('contexte_titre', restitution.contexte_titre)
        restitution.contexte_texte = request.POST.get('contexte_texte', restitution.contexte_texte)
        restitution.objectif_titre = request.POST.get('objectif_titre', restitution.objectif_titre)
        restitution.objectif_general = request.POST.get('objectif_general', restitution.objectif_general)
        restitution.resultats_titre = request.POST.get('resultats_titre', restitution.resultats_titre)
        restitution.resultats_intro = request.POST.get('resultats_intro', restitution.resultats_intro)
        restitution.public_titre_ceremonie = request.POST.get('public_titre_ceremonie', restitution.public_titre_ceremonie)

        contexte_points = request.POST.getlist('contexte_points')
        objectifs_specifiques = request.POST.getlist('objectifs_specifiques')
        resultats_attendus = request.POST.getlist('resultats_attendus')
        public_cible = request.POST.getlist('public_cible')

        restitution.contexte_points = [p for p in contexte_points if p.strip()]
        restitution.objectifs_specifiques = [p for p in objectifs_specifiques if p.strip()]
        restitution.resultats_attendus = [p for p in resultats_attendus if p.strip()]
        restitution.public_cible = [p for p in public_cible if p.strip()]

        # Section agenda
        restitution.agenda_titre = request.POST.get('agenda_titre', restitution.agenda_titre)
        restitution.agenda_label_duree = request.POST.get('agenda_label_duree', restitution.agenda_label_duree)
        restitution.agenda_label_date = request.POST.get('agenda_label_date', restitution.agenda_label_date)
        restitution.agenda_label_invites = request.POST.get('agenda_label_invites', restitution.agenda_label_invites)
        restitution.agenda_date = request.POST.get('agenda_date', restitution.agenda_date)
        restitution.agenda_duree = request.POST.get('agenda_duree', restitution.agenda_duree)
        restitution.agenda_invites = request.POST.get('agenda_invites', restitution.agenda_invites)
        restitution.agenda_empty_message = request.POST.get('agenda_empty_message', restitution.agenda_empty_message)

        agenda_heures = request.POST.getlist('agenda_session_heure')
        agenda_titres = request.POST.getlist('agenda_session_titre')
        agenda_details = request.POST.getlist('agenda_session_details')

        agenda_sessions = []
        max_len = max(len(agenda_heures), len(agenda_titres), len(agenda_details))
        for i in range(max_len):
            h = (agenda_heures[i] if i < len(agenda_heures) else '').strip()
            t = (agenda_titres[i] if i < len(agenda_titres) else '').strip()
            d = (agenda_details[i] if i < len(agenda_details) else '').strip()
            if h or t or d:
                agenda_sessions.append({'heure': h, 'titre': t, 'details': d})
        restitution.agenda_sessions = agenda_sessions
        
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

        # Galerie d'images (RestitutionImage position='galerie')
        galerie_ids = request.POST.getlist('galerie_id')
        for raw_id in galerie_ids:
            try:
                img_id = int(raw_id)
            except (TypeError, ValueError):
                continue

            try:
                img = RestitutionImage.objects.get(pk=img_id)
            except RestitutionImage.DoesNotExist:
                continue

            if request.POST.get(f'galerie_delete_{img_id}') == '1':
                img.delete()
                continue

            img.position = 'galerie'
            img.restitution = restitution
            img.titre = request.POST.get(f'galerie_titre_{img_id}', img.titre)
            img.description = request.POST.get(f'galerie_description_{img_id}', img.description)
            try:
                img.ordre = int(request.POST.get(f'galerie_ordre_{img_id}', img.ordre) or 0)
            except (TypeError, ValueError):
                pass
            img.active = request.POST.get(f'galerie_active_{img_id}') == 'on'
            img.image_url = request.POST.get(f'galerie_image_url_{img_id}', img.image_url)
            uploaded = request.FILES.get(f'galerie_image_{img_id}')
            if uploaded:
                img.image = uploaded
            img.save()

        new_titre = (request.POST.get('galerie_new_titre') or '').strip()
        new_desc = (request.POST.get('galerie_new_description') or '').strip()
        new_url = (request.POST.get('galerie_new_image_url') or '').strip()
        new_file = request.FILES.get('galerie_new_image')
        if new_file or new_url:
            try:
                new_ordre = int(request.POST.get('galerie_new_ordre') or 0)
            except (TypeError, ValueError):
                new_ordre = 0

            if not new_titre:
                new_titre = f"Image galerie #{new_ordre}"

            RestitutionImage.objects.create(
                restitution=restitution,
                titre=new_titre,
                description=new_desc,
                image=new_file,
                image_url=new_url,
                ordre=new_ordre,
                active=request.POST.get('galerie_new_active') == 'on',
                position='galerie',
            )
        elif request.POST.get('galerie_new_titre') is not None:
            messages.error(request, "Pour ajouter une image à la galerie, uploadez un fichier ou renseignez une URL.")
        
        restitution.save()
        messages.success(request, 'Les informations de restitution ont été mises à jour avec succès.')
        return redirect('admin_restitution')
    
    context = {
        'restitution': restitution,
        'page_title': 'Gestion Restitution',
        'galerie_images': list(
            RestitutionImage.objects.filter(restitution=restitution, position='galerie').order_by('ordre', 'date_ajout')
        ),
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
            contexte = (request.POST.get('contexte') or '').strip()
            objectif = (request.POST.get('objectif') or '').strip()
            questions_cles = (request.POST.get('questions_cles') or '').strip()
            intervenants = (request.POST.get('intervenants') or '').strip()
            lien_inscription = (request.POST.get('lien_inscription') or '').strip()
            image_url = (request.POST.get('image_url') or '').strip()
            ordre = int(request.POST.get('ordre') or 0)
            active = request.POST.get('active') == 'on'

            if not code or not label:
                messages.error(request, "Code et libellé sont obligatoires")
                return redirect('admin_ateliers')

            try:
                a = Atelier.objects.create(
                    code=code,
                    label=label,
                    description=description,
                    contexte=contexte,
                    objectif=objectif,
                    questions_cles=questions_cles,
                    intervenants=intervenants,
                    lien_inscription=lien_inscription,
                    ordre=ordre,
                    active=active,
                    image_url=image_url,
                )
                
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
                a.contexte = (request.POST.get('contexte') or '').strip()
                a.objectif = (request.POST.get('objectif') or '').strip()
                a.questions_cles = (request.POST.get('questions_cles') or '').strip()
                a.intervenants = (request.POST.get('intervenants') or '').strip()
                a.lien_inscription = (request.POST.get('lien_inscription') or '').strip()
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
                {'name': 'logo', 'label': 'Logo du site (navbar)', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Logo affiché dans la barre de navigation. Format PNG recommandé.'},
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
                {'name': '_sep_hero_about', 'label': '━━ Hero de la page À propos ━━', 'is_separator': True},
                {'name': 'page_about_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero de la page À propos.'},
                {'name': 'page_about_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle. Prioritaire sur l\'image.'},
                {'name': 'page_about_hero_badge', 'label': 'Texte du badge hero', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': '_sep_contenu_about', 'label': '━━ Contenu de la section ━━', 'is_separator': True},
                {'name': 'about_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
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
        'mot_ministre': {
            'titre': 'Mot de Madame la Ministre',
            'fields': [
                {'name': 'mot_ministre_image', 'label': 'Photo', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'mot_ministre_nom', 'label': 'Nom', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'mot_ministre_titre', 'label': 'Titre / Fonction', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'mot_ministre_texte', 'label': 'Texte du message', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Texte affiché sur la page À propos.'},
                {'name': 'mot_ministre_texte_size', 'label': 'Taille du texte', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 0.95rem, 1rem, 1.1rem'},
                {'name': 'mot_ministre_texte_bold', 'label': 'Texte en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_texte_italic', 'label': 'Texte en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_texte_font', 'label': 'Police', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_ministre_texte_color', 'label': 'Couleur du texte', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True, 'help_text': 'Couleur du texte du message'},
                {'name': '_sep_nom_ministre', 'label': '━━ Style du Nom ━━', 'is_separator': True},
                {'name': 'mot_ministre_nom_size', 'label': 'Taille du nom', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 1rem, 1.2rem'},
                {'name': 'mot_ministre_nom_bold', 'label': 'Nom en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_nom_italic', 'label': 'Nom en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_nom_font', 'label': 'Police du nom', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_ministre_nom_color', 'label': 'Couleur du nom', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True},
                {'name': '_sep_titre_ministre', 'label': '━━ Style du Titre/Fonction ━━', 'is_separator': True},
                {'name': 'mot_ministre_titre_size', 'label': 'Taille du titre', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 0.85rem, 0.9rem'},
                {'name': 'mot_ministre_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_ministre_titre_font', 'label': 'Police du titre', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_ministre_titre_color', 'label': 'Couleur du titre', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True},
            ],
        },
        'mot_professeur': {
            'titre': 'Mot du Professeur Baniré',
            'fields': [
                {'name': 'mot_professeur_image', 'label': 'Photo', 'is_textarea': False, 'is_url': False, 'is_image': True},
                {'name': 'mot_professeur_nom', 'label': 'Nom', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'mot_professeur_titre', 'label': 'Titre / Fonction', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'mot_professeur_texte', 'label': 'Texte du message', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Texte affiché sur la page À propos.'},
                {'name': 'mot_professeur_texte_size', 'label': 'Taille du texte', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 0.95rem, 1rem, 1.1rem'},
                {'name': 'mot_professeur_texte_bold', 'label': 'Texte en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_texte_italic', 'label': 'Texte en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_texte_font', 'label': 'Police', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_professeur_texte_color', 'label': 'Couleur du texte', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True, 'help_text': 'Couleur du texte du message'},
                {'name': '_sep_nom_prof', 'label': '━━ Style du Nom ━━', 'is_separator': True},
                {'name': 'mot_professeur_nom_size', 'label': 'Taille du nom', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 1rem, 1.2rem'},
                {'name': 'mot_professeur_nom_bold', 'label': 'Nom en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_nom_italic', 'label': 'Nom en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_nom_font', 'label': 'Police du nom', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_professeur_nom_color', 'label': 'Couleur du nom', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True},
                {'name': '_sep_titre_prof', 'label': '━━ Style du Titre/Fonction ━━', 'is_separator': True},
                {'name': 'mot_professeur_titre_size', 'label': 'Taille du titre', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Ex: 0.85rem, 0.9rem'},
                {'name': 'mot_professeur_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'mot_professeur_titre_font', 'label': 'Police du titre', 'is_select': True, 'is_textarea': False, 'is_url': False, 'is_image': False, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Roboto', sans-serif", 'Roboto'), ("'Playfair Display', serif", 'Playfair Display'), ("'Inter', sans-serif", 'Inter'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'mot_professeur_titre_color', 'label': 'Couleur du titre', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_color': True},
            ],
        },
        'dounia1': {
            'titre': 'DounIA 1',
            'fields': [
                {'name': 'dounia1_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'dounia1_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'dounia1_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'dounia1_defis', 'label': 'Défis (un par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Un défi par ligne'},
                {'name': 'dounia1_opportunites', 'label': 'Opportunités (une par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Une opportunité par ligne'},
            ],
        },
        'rapport': {
            'titre': 'Rapport DounIA 1',
            'fields': [
                {'name': '_sep_hero_livrable', 'label': '━━ Hero de la page Livrable ━━', 'is_separator': True},
                {'name': 'page_livrable_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image arrière-plan du hero de la page Livrable.'},
                {'name': 'page_livrable_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 en boucle. Prioritaire sur l\'image.'},
                {'name': 'page_livrable_hero_badge', 'label': 'Texte du badge hero', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': '_sep_contenu_livrable', 'label': '━━ Contenu de la section ━━', 'is_separator': True},
                {'name': 'rapport_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'rapport_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'rapport_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'rapport_description', 'label': 'Description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'rapport_points', 'label': 'Points clés (un par ligne)', 'is_textarea': True, 'is_url': False, 'is_image': False, 'help_text': 'Un point par ligne'},
                {'name': 'rapport_fichier', 'label': 'Fichier PDF du rapport (upload direct)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': True, 'help_text': 'Uploadez directement le fichier PDF. Priorité au lien externe ci-dessous si les deux sont renseignés.'},
                {'name': 'rapport_lien', 'label': 'Lien de téléchargement du rapport (URL externe)', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'URL vers le PDF (Google Drive, Dropbox, etc.). Prioritaire sur le fichier uploadé.'},
                {'name': 'rapport_image', 'label': 'Image de couverture du rapport', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée à gauche du rapport sur la page d\'accueil.'},
            ],
        },

        'evenements': {
            'titre': 'Événements (section landing)',
            'fields': [
                {'name': '_sep_hero_evenements', 'label': '━━ Hero de la page Événements ━━', 'is_separator': True},
                {'name': 'page_evenements_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image arrière-plan du hero de la page Événements.'},
                {'name': 'page_evenements_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 en boucle. Prioritaire sur l\'image.'},
                {'name': 'page_evenements_hero_badge', 'label': 'Texte du badge hero', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': '_sep_contenu_evenements', 'label': '━━ Contenu de la section ━━', 'is_separator': True},
                {'name': 'evenements_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
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
                {'name': 'podcast_video', 'label': 'Vidéo format téléphone (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Uploadez une vidéo MP4 en format portrait (vertical). Elle s\'affichera dans un cadre téléphone.'},
                {'name': 'podcast_video_url', 'label': 'URL vidéo (YouTube embed, optionnel)', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'URL embed d\'une vidéo YouTube/Vimeo. Utilisé si aucun fichier vidéo n\'est uploadé.'},
            ],
        },
        'galerie_videos': {
            'titre': 'Galerie Vidéos (Podcast)',
            'fields': [
                {'name': '_sep_hero_podcast', 'label': '━━ Hero de la page Podcast ━━', 'is_separator': True},
                {'name': 'page_podcast_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image arrière-plan du hero de la page Podcast.'},
                {'name': 'page_podcast_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 en boucle. Prioritaire sur l\'image.'},
                {'name': 'page_podcast_hero_badge', 'label': 'Texte du badge hero', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': '_sep_contenu_podcast', 'label': '━━ Contenu de la section ━━', 'is_separator': True},
                {'name': 'galerie_videos_titre', 'label': 'Titre de la section', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'podcast_youtube_url', 'label': 'Lien YouTube CSIG (bouton "Voir plus")', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'URL de la chaîne YouTube CSIG. Ex: https://www.youtube.com/@csig-guinee'},
                {'name': 'galerie_video_1', 'label': 'Vidéo 1 (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Vidéo portrait format téléphone'},
                {'name': 'galerie_video_2', 'label': 'Vidéo 2 (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Vidéo portrait format téléphone'},
                {'name': 'galerie_video_3', 'label': 'Vidéo 3 (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Vidéo portrait format téléphone'},
                {'name': 'galerie_video_4', 'label': 'Vidéo 4 (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Vidéo portrait format téléphone'},
                {'name': 'galerie_video_5', 'label': 'Vidéo 5 (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Vidéo portrait format téléphone'},
            ],
        },
        'dounia2': {
            'titre': 'DounIA 2',
            'fields': [
                {'name': 'dounia2_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
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
                {'name': 'experts_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'experts_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'experts_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },

        'ateliers_section': {
            'titre': 'Ateliers (section landing)',
            'fields': [
                {'name': '_sep_hero_ateliers', 'label': '━━ Hero de la page Ateliers ━━', 'is_separator': True},
                {'name': 'page_ateliers_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image arrière-plan du hero de la page Ateliers.'},
                {'name': 'page_ateliers_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 en boucle. Prioritaire sur l\'image.'},
                {'name': 'page_ateliers_hero_badge', 'label': 'Texte du badge hero', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': '_sep_contenu_ateliers', 'label': '━━ Contenu de la section ━━', 'is_separator': True},
                {'name': 'ateliers_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'ateliers_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'ateliers_sous_titre', 'label': 'Sous-titre', 'is_textarea': True, 'is_url': False, 'is_image': False},
            ],
        },

        'calendrier_section': {
            'titre': 'Calendrier (section landing)',
            'fields': [
                {'name': 'calendrier_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
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
                {'name': 'video_fichier', 'label': 'Fichier vidéo MP4 (optionnel)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': False, 'is_video': True, 'help_text': 'Uploadez un fichier MP4. Ce fichier sera prioritaire sur le lien YouTube.'},
            ],
        },
        'inscription_section': {
            'titre': 'Section Inscription',
            'fields': [
                {'name': 'inscription_align', 'label': 'Alignement du texte', 'is_select': True, 'choices': [('center', 'Centré'), ('left', 'Gauche'), ('right', 'Droite'), ('justify', 'Justifié')], 'is_textarea': False, 'is_url': False, 'is_image': False},
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
        'countdown': {
            'titre': 'Compte à rebours',
            'fields': [
                {'name': 'countdown_actif', 'label': 'Activer le compte à rebours', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True, 'help_text': 'Cochez pour afficher le compte à rebours dans le hero. Décochez pour le masquer définitivement.'},
                {'name': 'date_lancement_site', 'label': 'Date de lancement du site', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_datetime': True, 'help_text': "Date et heure du lancement officiel. Le compte à rebours s'affichera dans le hero. Laissez vide pour désactiver."},
            ],
        },
        'splash': {
            'titre': 'Écran de chargement (Splash)',
            'fields': [
                {'name': 'splash_actif', 'label': 'Activer l\'écran de chargement (Splash)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True, 'help_text': 'Cochez pour afficher le splash screen au chargement. Décochez pour le désactiver définitivement.'},
                {'name': 'splash_duree', 'label': 'Durée du décompte (secondes)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_integer': True, 'help_text': 'Nombre de secondes du décompte avant l\'ouverture du site. Ex: 30'},
                {'name': 'splash_audio_file', 'label': 'Fichier audio (MP3)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_file': True, 'help_text': 'Uploadez votre propre fichier MP3. Prioritaire sur l\'URL ci-dessous.'},
                {'name': 'splash_audio_url', 'label': 'URL audio (si pas de fichier)', 'is_textarea': False, 'is_url': True, 'is_image': False, 'help_text': 'Lien direct vers un MP3 en ligne. Ignoré si un fichier est uploadé.'},
            ],
        },
        'hero_slides_style': {
            'titre': 'Slides Hero — Style du texte',
            'fields': [
                {'name': 'hero_slide_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'hero_slide_titre_size', 'label': 'Taille du titre (ex: 2.4rem, 36px)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Exemples : 2rem, 2.4rem, 3rem, 28px, 36px'},
                {'name': 'hero_slide_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'hero_slide_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'hero_slide_desc_size', 'label': 'Taille de la description (ex: 1.05rem, 16px)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'help_text': 'Exemples : 1rem, 1.1rem, 14px, 16px'},
                {'name': 'hero_slide_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'hero_slide_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
            ],
        },
        'page_about': {
            'titre': 'Page À propos',
            'fields': [
                {'name': 'page_about_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero.'},
                {'name': 'page_about_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle en arrière-plan du hero. Prioritaire sur l\'image.'},
                {'name': 'page_about_hero_badge', 'label': 'Texte du badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'about_sous_titre', 'label': 'Sous-titre / description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'page_about_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'page_about_titre_size', 'label': 'Taille du titre (ex: 2.4rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_about_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_about_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_about_desc_size', 'label': 'Taille description (ex: 1.05rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_about_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_about_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
            ],
        },
        'page_ateliers': {
            'titre': 'Page Ateliers',
            'fields': [
                {'name': 'page_ateliers_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero.'},
                {'name': 'page_ateliers_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle en arrière-plan du hero. Prioritaire sur l\'image.'},
                {'name': 'page_ateliers_hero_badge', 'label': 'Texte du badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'ateliers_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'ateliers_sous_titre', 'label': 'Sous-titre / description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'page_ateliers_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'page_ateliers_titre_size', 'label': 'Taille du titre (ex: 2.4rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_ateliers_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_ateliers_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_ateliers_desc_size', 'label': 'Taille description (ex: 1.05rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_ateliers_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_ateliers_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
            ],
        },
        'page_evenements': {
            'titre': 'Page Événements',
            'fields': [
                {'name': 'page_evenements_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero.'},
                {'name': 'page_evenements_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle en arrière-plan du hero. Prioritaire sur l\'image.'},
                {'name': 'page_evenements_hero_badge', 'label': 'Texte du badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'evenements_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'evenements_sous_titre', 'label': 'Sous-titre / description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'page_evenements_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'page_evenements_titre_size', 'label': 'Taille du titre (ex: 2.4rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_evenements_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_evenements_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_evenements_desc_size', 'label': 'Taille description (ex: 1.05rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_evenements_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_evenements_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
            ],
        },
        'page_podcast': {
            'titre': 'Page Podcast',
            'fields': [
                {'name': 'page_podcast_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero.'},
                {'name': 'page_podcast_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle en arrière-plan du hero. Prioritaire sur l\'image.'},
                {'name': 'page_podcast_hero_badge', 'label': 'Texte du badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'galerie_videos_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_podcast_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'page_podcast_titre_size', 'label': 'Taille du titre (ex: 2.4rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_podcast_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_podcast_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_podcast_desc_size', 'label': 'Taille description (ex: 1.05rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_podcast_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_podcast_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
            ],
        },
        'page_livrable': {
            'titre': 'Page Livrable',
            'fields': [
                {'name': 'page_livrable_hero_image', 'label': 'Image de fond du hero', 'is_textarea': False, 'is_url': False, 'is_image': True, 'help_text': 'Image affichée en arrière-plan du hero.'},
                {'name': 'page_livrable_hero_video', 'label': 'Vidéo de fond du hero (MP4)', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_video': True, 'help_text': 'Vidéo MP4 jouée en boucle en arrière-plan du hero. Prioritaire sur l\'image.'},
                {'name': 'page_livrable_hero_badge', 'label': 'Texte du badge', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'rapport_titre', 'label': 'Titre', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'rapport_sous_titre', 'label': 'Sous-titre / description', 'is_textarea': True, 'is_url': False, 'is_image': False},
                {'name': 'page_livrable_font', 'label': 'Police', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_select': True, 'choices': [('inherit', 'Par défaut'), ("'Poppins', sans-serif", 'Poppins'), ("'Montserrat', sans-serif", 'Montserrat'), ("'Playfair Display', serif", 'Playfair Display'), ("'Roboto', sans-serif", 'Roboto'), ("'Raleway', sans-serif", 'Raleway'), ("'Oswald', sans-serif", 'Oswald'), ("'Lora', serif", 'Lora')]},
                {'name': 'page_livrable_titre_size', 'label': 'Taille du titre (ex: 2.4rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_livrable_titre_bold', 'label': 'Titre en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_livrable_titre_italic', 'label': 'Titre en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_livrable_desc_size', 'label': 'Taille description (ex: 1.05rem)', 'is_textarea': False, 'is_url': False, 'is_image': False},
                {'name': 'page_livrable_desc_bold', 'label': 'Description en gras', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
                {'name': 'page_livrable_desc_italic', 'label': 'Description en italique', 'is_textarea': False, 'is_url': False, 'is_image': False, 'is_boolean': True},
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
        alignments = dict(config.text_alignments or {})
        for field in section_def['fields']:
            if field.get('is_separator'):
                continue
            name = field['name']
            if field.get('is_file') or field.get('is_image') or field.get('is_video'):
                uploaded = request.FILES.get(name)
                if uploaded:
                    setattr(config, name, uploaded)
            else:
                value = request.POST.get(name, '')
                if field.get('is_datetime'):
                    if value:
                        from datetime import datetime as dt
                        try:
                            setattr(config, name, dt.strptime(value, '%Y-%m-%dT%H:%M'))
                        except ValueError:
                            pass
                    else:
                        setattr(config, name, None)
                elif field.get('is_boolean'):
                    setattr(config, name, name in request.POST)
                elif field.get('is_integer'):
                    try:
                        setattr(config, name, int(value))
                    except (ValueError, TypeError):
                        pass
                else:
                    setattr(config, name, value)
                if field.get('is_textarea'):
                    align_val = request.POST.get(name + '__align', 'left')
                    if align_val in ('left', 'center', 'right', 'justify'):
                        alignments[name] = align_val
        config.text_alignments = alignments
        config.save()
        messages.success(request, f'Section "{section_def["titre"]}" mise à jour avec succès')
        return redirect('admin_contenu_page')

    # Build fields_data with current values
    _align_choices = [('left', 'Gauche'), ('center', 'Centré'), ('right', 'Droite'), ('justify', 'Justifié')]
    _alignments = config.text_alignments or {}
    fields_data = []
    for field in section_def['fields']:
        fd = dict(field)
        val = getattr(config, field['name'], '')
        if field.get('is_datetime') and val:
            fd['value'] = val.strftime('%Y-%m-%dT%H:%M')
        else:
            fd['value'] = val
        if 'help_text' not in fd:
            fd['help_text'] = ''
        if field.get('is_textarea'):
            fd['align_value'] = _alignments.get(field['name'], 'left')
            fd['align_choices'] = _align_choices
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
    """Export des inscriptions en CSV Excel-compatible (UTF-8 BOM, séparateur ;)"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="inscriptions_dounia.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'N°', 'Nom', 'Prénom', 'Email', 'WhatsApp', 'Institution', 'Fonction',
        'Profil', 'Atelier', 'Engagement', 'Format', 'Disponibilité', 'Motivation', 'Date',
    ])

    inscriptions = Inscription.objects.all().order_by('-date_inscription')
    for idx, insc in enumerate(inscriptions, 1):
        writer.writerow([
            idx,
            insc.nom,
            insc.prenom,
            insc.email,
            insc.whatsapp or '',
            insc.institution,
            insc.fonction,
            insc.get_profil_display(),
            insc.atelier_label,
            insc.get_engagement_display(),
            insc.get_format_preference_display(),
            insc.get_disponibilite_display(),
            insc.motivation or '',
            insc.date_inscription.strftime('%d/%m/%Y %H:%M'),
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


@require_POST
def soumettre_avis(request):
    """API pour soumettre un avis depuis le chat"""
    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    
    nom = data.get('nom', '').strip()
    email = data.get('email', '').strip()
    telephone = data.get('telephone', '').strip()
    message = data.get('message', '').strip()
    event_slug = data.get('event_slug', 'dounia1')
    
    if not nom or not message:
        return JsonResponse({'success': False, 'error': 'Le nom et le message sont requis.'}, status=400)
    
    Avis.objects.create(
        nom=nom,
        email=email,
        telephone=telephone,
        message=message,
        event_slug=event_slug,
    )
    return JsonResponse({'success': True, 'message': 'Merci pour votre avis !'})


@staff_required
def admin_avis(request):
    """Page admin pour voir les avis"""
    avis_list = Avis.objects.all()
    
    # Filtres
    event_filter = request.GET.get('event', '')
    lu_filter = request.GET.get('lu', '')
    q = request.GET.get('q', '')
    
    if event_filter:
        avis_list = avis_list.filter(event_slug=event_filter)
    if lu_filter == '0':
        avis_list = avis_list.filter(lu=False)
    elif lu_filter == '1':
        avis_list = avis_list.filter(lu=True)
    if q:
        avis_list = avis_list.filter(
            Q(nom__icontains=q) | Q(email__icontains=q) | Q(message__icontains=q)
        )
    
    # Marquer comme lu
    if request.method == 'POST':
        action = request.POST.get('action')
        pk = request.POST.get('pk')
        if action == 'toggle_lu' and pk:
            try:
                avis = Avis.objects.get(pk=pk)
                avis.lu = not avis.lu
                avis.save()
                messages.success(request, f"Avis de {avis.nom} marqué comme {'lu' if avis.lu else 'non lu'}.")
            except Avis.DoesNotExist:
                pass
        elif action == 'delete' and pk:
            Avis.objects.filter(pk=pk).delete()
            messages.success(request, "Avis supprimé.")
        return redirect('admin_avis')
    
    context = {
        'avis_list': avis_list,
        'total': avis_list.count(),
        'non_lus': Avis.objects.filter(lu=False).count(),
        'event_filter': event_filter,
        'lu_filter': lu_filter,
        'q': q,
    }
    return render(request, 'gestion/avis.html', context)


@staff_required
def admin_users(request):
    """Page admin pour gérer les utilisateurs"""
    from django.contrib.auth.models import User

    users = User.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if role_filter == 'staff':
        users = users.filter(is_staff=True)
    elif role_filter == 'superuser':
        users = users.filter(is_superuser=True)
    elif role_filter == 'normal':
        users = users.filter(is_staff=False, is_superuser=False)

    context = {
        'users': users,
        'total': User.objects.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'superuser_count': User.objects.filter(is_superuser=True).count(),
        'q': q,
        'role_filter': role_filter,
    }
    return render(request, 'gestion/users.html', context)


@staff_required
def admin_user_create(request):
    """Créer un nouvel utilisateur"""
    from django.contrib.auth.models import User

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        is_staff = 'is_staff' in request.POST
        is_superuser = 'is_superuser' in request.POST
        is_active = 'is_active' in request.POST

        errors = []
        if not username:
            errors.append("Le nom d'utilisateur est obligatoire.")
        elif User.objects.filter(username=username).exists():
            errors.append(f"Le nom d'utilisateur « {username} » existe déjà.")
        if not password:
            errors.append("Le mot de passe est obligatoire.")
        elif len(password) < 6:
            errors.append("Le mot de passe doit contenir au moins 6 caractères.")
        elif password != password2:
            errors.append("Les deux mots de passe ne correspondent pas.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'gestion/user_form.html', {
                'mode': 'create',
                'form_data': request.POST,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = is_active
        user.save()
        messages.success(request, f"Utilisateur « {username} » créé avec succès.")
        return redirect('admin_users')

    return render(request, 'gestion/user_form.html', {
        'mode': 'create',
        'form_data': {},
    })


@staff_required
def admin_user_edit(request, pk):
    """Modifier un utilisateur existant"""
    from django.contrib.auth.models import User

    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        is_staff = 'is_staff' in request.POST
        is_superuser = 'is_superuser' in request.POST
        is_active = 'is_active' in request.POST

        errors = []
        if not username:
            errors.append("Le nom d'utilisateur est obligatoire.")
        elif User.objects.filter(username=username).exclude(pk=pk).exists():
            errors.append(f"Le nom d'utilisateur « {username} » est déjà pris.")
        if password and len(password) < 6:
            errors.append("Le mot de passe doit contenir au moins 6 caractères.")
        elif password and password != password2:
            errors.append("Les deux mots de passe ne correspondent pas.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'gestion/user_form.html', {
                'mode': 'edit',
                'user_obj': user_obj,
                'form_data': request.POST,
            })

        user_obj.username = username
        user_obj.email = email
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.is_active = is_active
        if password:
            user_obj.set_password(password)
        user_obj.save()
        messages.success(request, f"Utilisateur « {username} » mis à jour.")
        return redirect('admin_users')

    return render(request, 'gestion/user_form.html', {
        'mode': 'edit',
        'user_obj': user_obj,
        'form_data': {
            'username': user_obj.username,
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'is_staff': user_obj.is_staff,
            'is_superuser': user_obj.is_superuser,
            'is_active': user_obj.is_active,
        },
    })


@staff_required
def admin_user_delete(request, pk):
    """Supprimer un utilisateur"""
    from django.contrib.auth.models import User

    user_obj = get_object_or_404(User, pk=pk)

    if user_obj == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('admin_users')

    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"Utilisateur « {username} » supprimé.")
        return redirect('admin_users')

    return render(request, 'gestion/user_confirm_delete.html', {
        'user_obj': user_obj,
    })


# ==========================================================================
# MODULE ARTICLES (publication façon WordPress)
# ==========================================================================

def _parse_article_post(request, article):
    """Remplit un objet Article à partir des données POST (création ou édition)."""
    article.titre = (request.POST.get('titre') or '').strip()
    slug = (request.POST.get('slug') or '').strip()
    if slug:
        article.slug = slugify(slug)
    article.chapo = (request.POST.get('chapo') or '').strip()
    article.corps = request.POST.get('corps') or ''
    article.image_url = (request.POST.get('image_url') or '').strip()
    article.image_legende = (request.POST.get('image_legende') or '').strip()
    article.tags = (request.POST.get('tags') or '').strip()
    article.auteur_nom = (request.POST.get('auteur_nom') or '').strip()
    article.meta_title = (request.POST.get('meta_title') or '').strip()
    article.meta_description = (request.POST.get('meta_description') or '').strip()

    statut = request.POST.get('statut') or 'brouillon'
    if statut not in dict(Article.STATUT_CHOICES):
        statut = 'brouillon'
    article.statut = statut

    visibilite = request.POST.get('visibilite') or 'public'
    if visibilite not in dict(Article.VISIBILITE_CHOICES):
        visibilite = 'public'
    article.visibilite = visibilite

    article.epingle = request.POST.get('epingle') == 'on'
    article.autoriser_commentaires = request.POST.get('autoriser_commentaires') == 'on'

    # Affichage sur le site
    article.afficher_accueil = request.POST.get('afficher_accueil') == 'on'
    article.afficher_ateliers = request.POST.get('afficher_ateliers') == 'on'
    article.afficher_evenements = request.POST.get('afficher_evenements') == 'on'
    article.afficher_podcast = request.POST.get('afficher_podcast') == 'on'
    article.afficher_livrables = request.POST.get('afficher_livrables') == 'on'
    article.afficher_apropos = request.POST.get('afficher_apropos') == 'on'

    # Rubrique
    rubrique_id = request.POST.get('rubrique')
    if rubrique_id:
        article.rubrique = Rubrique.objects.filter(pk=rubrique_id).first()
    else:
        article.rubrique = None

    # Date de publication
    date_pub = (request.POST.get('date_publication') or '').strip()
    if date_pub:
        parsed = parse_datetime(date_pub)
        if parsed is not None:
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            article.date_publication = parsed
    elif not article.date_publication:
        article.date_publication = timezone.now()

    return article


@staff_required
def admin_articles(request):
    """Liste des articles avec recherche et filtres."""
    articles = Article.objects.select_related('rubrique', 'auteur').all()

    q = request.GET.get('q', '')
    statut_filter = request.GET.get('statut', '')
    rubrique_filter = request.GET.get('rubrique', '')

    if q:
        articles = articles.filter(
            Q(titre__icontains=q) | Q(chapo__icontains=q) |
            Q(corps__icontains=q) | Q(tags__icontains=q)
        )
    if statut_filter in dict(Article.STATUT_CHOICES):
        articles = articles.filter(statut=statut_filter)
    if rubrique_filter:
        articles = articles.filter(rubrique_id=rubrique_filter)

    context = {
        'articles': articles,
        'total': Article.objects.count(),
        'publies': Article.objects.filter(statut='publie').count(),
        'brouillons': Article.objects.filter(statut='brouillon').count(),
        'programmes': Article.objects.filter(statut='programme').count(),
        'rubriques': Rubrique.objects.all(),
        'statut_choices': Article.STATUT_CHOICES,
        'q': q,
        'statut_filter': statut_filter,
        'rubrique_filter': rubrique_filter,
    }
    return render(request, 'gestion/articles.html', context)


@staff_required
def admin_article_create(request):
    """Créer un nouvel article."""
    if request.method == 'POST':
        article = Article()
        _parse_article_post(request, article)

        if not article.titre:
            messages.error(request, "Le titre est obligatoire.")
            return render(request, 'gestion/article_form.html', _article_form_context('create', article))

        article.auteur = request.user
        article.save()

        if 'image' in request.FILES:
            uploaded = request.FILES['image']
            if uploaded.size > 5 * 1024 * 1024:
                messages.warning(request, "Image trop volumineuse (max 5MB), elle n'a pas été enregistrée.")
            else:
                article.image = uploaded
                article.save()

        messages.success(request, f"Article « {article.titre} » créé ({article.get_statut_display()}).")
        return redirect('admin_articles')

    article = Article(date_publication=timezone.now())
    return render(request, 'gestion/article_form.html', _article_form_context('create', article))


@staff_required
def admin_article_edit(request, pk):
    """Modifier un article existant."""
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        _parse_article_post(request, article)

        if not article.titre:
            messages.error(request, "Le titre est obligatoire.")
            return render(request, 'gestion/article_form.html', _article_form_context('edit', article))

        if 'image' in request.FILES:
            uploaded = request.FILES['image']
            if uploaded.size > 5 * 1024 * 1024:
                messages.warning(request, "Image trop volumineuse (max 5MB), non remplacée.")
            else:
                article.image = uploaded
        if request.POST.get('supprimer_image') == 'on':
            article.image = None

        article.save()
        messages.success(request, f"Article « {article.titre} » mis à jour.")
        return redirect('admin_articles')

    return render(request, 'gestion/article_form.html', _article_form_context('edit', article))


@staff_required
def admin_article_delete(request, pk):
    """Supprimer un article."""
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        titre = article.titre
        article.delete()
        messages.success(request, f"Article « {titre} » supprimé.")
    return redirect('admin_articles')


@staff_required
@require_POST
def admin_article_toggle(request, pk):
    """Basculer rapidement le statut publié/brouillon ou l'épinglage d'un article."""
    article = get_object_or_404(Article, pk=pk)
    field = request.POST.get('field')
    if field == 'epingle':
        article.epingle = not article.epingle
        article.save(update_fields=['epingle'])
        messages.success(request, f"« {article.titre} » {'épinglé' if article.epingle else 'désépinglé'}.")
    else:
        if article.statut == 'publie':
            article.statut = 'brouillon'
        else:
            article.statut = 'publie'
            if article.date_publication > timezone.now():
                article.date_publication = timezone.now()
        article.save(update_fields=['statut', 'date_publication'])
        messages.success(request, f"« {article.titre} » → {article.get_statut_display()}.")
    return redirect('admin_articles')


def _article_form_context(mode, article):
    return {
        'mode': mode,
        'article': article,
        'rubriques': Rubrique.objects.all(),
        'statut_choices': Article.STATUT_CHOICES,
        'visibilite_choices': Article.VISIBILITE_CHOICES,
    }


@staff_required
def admin_rubriques(request):
    """Gestion des rubriques (catégories) des articles."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            nom = (request.POST.get('nom') or '').strip()
            if not nom:
                messages.error(request, "Le nom de la rubrique est obligatoire.")
            else:
                Rubrique.objects.create(
                    nom=nom,
                    description=(request.POST.get('description') or '').strip(),
                    couleur=(request.POST.get('couleur') or '#003366').strip(),
                    ordre=int(request.POST.get('ordre') or 0),
                    active=request.POST.get('active') == 'on',
                )
                messages.success(request, f"Rubrique « {nom} » ajoutée.")
        elif action == 'edit':
            r = Rubrique.objects.filter(pk=request.POST.get('pk')).first()
            if r:
                r.nom = (request.POST.get('nom') or r.nom).strip()
                r.description = (request.POST.get('description') or '').strip()
                r.couleur = (request.POST.get('couleur') or '#003366').strip()
                r.ordre = int(request.POST.get('ordre') or 0)
                r.active = request.POST.get('active') == 'on'
                r.save()
                messages.success(request, f"Rubrique « {r.nom} » mise à jour.")
        elif action == 'delete':
            Rubrique.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, "Rubrique supprimée.")
        return redirect('admin_rubriques')

    context = {
        'rubriques': Rubrique.objects.all(),
    }
    return render(request, 'gestion/rubriques.html', context)


# ==========================================================================
# PAGES PUBLIQUES — ACTUALITÉS
# ==========================================================================

def actualites_page(request):
    """Liste publique des articles publiés (page Actualités)."""
    config = SiteConfiguration.get()
    articles = Article.objects.select_related('rubrique', 'auteur').filter(
        statut='publie', visibilite='public', date_publication__lte=timezone.now()
    )

    q = request.GET.get('q', '')
    rubrique_slug = request.GET.get('rubrique', '')
    if q:
        articles = articles.filter(
            Q(titre__icontains=q) | Q(chapo__icontains=q) | Q(tags__icontains=q)
        )
    if rubrique_slug:
        articles = articles.filter(rubrique__slug=rubrique_slug)

    epingles = articles.filter(epingle=True)[:3]

    context = {
        'config': config,
        'articles': articles,
        'epingles': epingles,
        'rubriques': Rubrique.objects.filter(active=True),
        'q': q,
        'rubrique_slug': rubrique_slug,
    }
    return render(request, 'actualites.html', context)


def article_detail(request, slug):
    """Page de détail d'un article publié."""
    config = SiteConfiguration.get()
    article = get_object_or_404(
        Article.objects.select_related('rubrique', 'auteur'), slug=slug
    )

    # Sécurité de visibilité
    if not article.est_en_ligne:
        if not (request.user.is_authenticated and request.user.is_staff):
            if article.visibilite == 'membres' and request.user.is_authenticated:
                pass
            else:
                from django.http import Http404
                raise Http404("Article non disponible")

    # Incrémenter les vues (hors staff)
    if not (request.user.is_authenticated and request.user.is_staff):
        Article.objects.filter(pk=article.pk).update(vues=models.F('vues') + 1)

    articles_similaires = Article.objects.filter(
        statut='publie', visibilite='public', date_publication__lte=timezone.now()
    ).exclude(pk=article.pk)
    if article.rubrique_id:
        articles_similaires = articles_similaires.filter(rubrique_id=article.rubrique_id)
    articles_similaires = articles_similaires[:3]

    context = {
        'config': config,
        'article': article,
        'articles_similaires': articles_similaires,
    }
    return render(request, 'article_detail.html', context)


# ═══════════════════════════════════════════════════════════════════
# MODULE ACCÈS — Inscription Conférence + Badge PDF
# ═══════════════════════════════════════════════════════════════════

def inscription_conference(request):
    """Page publique d'inscription à la conférence DounIA."""
    config = SiteConfiguration.objects.first()
    if request.method == 'POST':
        form = InscriptionConferenceForm(request.POST)
        if form.is_valid():
            inscrit = form.save()
            return redirect('conference_merci', identifiant=inscrit.identifiant)
    else:
        form = InscriptionConferenceForm()

    return render(request, 'inscriptions/conference_inscription.html', {
        'config': config,
        'form': form,
    })


def conference_merci(request, identifiant):
    """Page de confirmation après inscription à la conférence."""
    config = SiteConfiguration.objects.first()
    try:
        inscrit = InscriptionConference.objects.get(identifiant=identifiant)
    except InscriptionConference.DoesNotExist:
        messages.error(request,
            "L'inscription demandée n'a pas été trouvée. "
            "Veuillez vérifier l'identifiant ou vous inscrire à la conférence.")
        return redirect('inscription_conference')
    return render(request, 'inscriptions/conference_merci.html', {
        'config': config,
        'inscrit': inscrit,
    })


def conference_badge_download(request, identifiant):
    """Téléchargement du badge PDF — uniquement si l'inscription est validée."""
    inscrit = get_object_or_404(InscriptionConference, identifiant=identifiant)

    if not inscrit.valide:
        messages.warning(request, "Votre inscription n'a pas encore été validée. Le badge sera disponible après validation.")
        return redirect('conference_merci', identifiant=identifiant)

    if not inscrit.badge_pdf:
        messages.error(request, "Le badge n'est pas encore disponible.")
        return redirect('conference_merci', identifiant=identifiant)

    import os
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(inscrit.badge_pdf))
    if not os.path.exists(pdf_path):
        messages.error(request, "Le fichier badge est introuvable.")
        return redirect('conference_merci', identifiant=identifiant)

    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="badge_{inscrit.identifiant}.pdf"'
        return response


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_conference_inscriptions(request):
    """Liste des inscriptions à la conférence (admin)."""
    config = SiteConfiguration.objects.first()
    inscriptions = InscriptionConference.objects.all()

    # Filtres
    categorie = request.GET.get('categorie', '')
    search = request.GET.get('q', '')
    if categorie:
        inscriptions = inscriptions.filter(categorie=categorie)
    if search:
        inscriptions = inscriptions.filter(
            Q(nom__icontains=search) | Q(prenom__icontains=search) |
            Q(email__icontains=search) | Q(identifiant__icontains=search)
        )

    # Stats
    stats = {
        'total': InscriptionConference.objects.count(),
        'valides': InscriptionConference.objects.filter(valide=True).count(),
        'par_categorie': InscriptionConference.objects.values('categorie').annotate(
            count=Count('id')
        ).order_by('categorie'),
    }

    # Templates de badges uploadés
    badge_templates = BadgeTemplate.objects.all()
    categories_avec_template = set(badge_templates.values_list('categorie', flat=True))

    return render(request, 'gestion/conference_inscriptions.html', {
        'config': config,
        'inscriptions': inscriptions,
        'stats': stats,
        'categorie_filter': categorie,
        'search_query': search,
        'categories': InscriptionConference.CATEGORIE_CHOICES,
        'badge_templates': badge_templates,
        'categories_avec_template': categories_avec_template,
    })


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_conference_valider(request, pk):
    """Valider une inscription conférence, générer le badge PDF et l'envoyer par email."""
    inscrit = get_object_or_404(InscriptionConference, pk=pk)
    inscrit.valide = True
    inscrit.date_validation = timezone.now()
    inscrit.save(update_fields=['valide', 'date_validation'])

    pdf_path = None

    # Générer le badge PDF à la validation
    try:
        from .generer_badge import generer_badge
        import os
        pdf_path = generer_badge(
            nom=inscrit.nom, prenom=inscrit.prenom,
            categorie=inscrit.categorie, identifiant=inscrit.identifiant,
        )
        rel_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
        inscrit.badge_pdf = rel_path
        inscrit.save(update_fields=['badge_pdf'])
    except Exception as e:
        messages.warning(request,
            f"Inscription validée mais le badge n'a pas pu être généré : {e}")
        return redirect('admin_conference_inscriptions')

    # Envoyer le badge par email au participant + copie à l'admin
    try:
        admin_email = settings.DEFAULT_FROM_EMAIL
        categorie_label = inscrit.get_categorie_display()

        # Email au participant
        email_participant = EmailMessage(
            subject=f"Conférence DounIA — Votre badge {categorie_label} est prêt",
            body=(
                f"Bonjour {inscrit.prenom},\n\n"
                f"Votre inscription à la Conférence DounIA a été validée.\n\n"
                f"Catégorie : {categorie_label}\n"
                f"Identifiant : {inscrit.identifiant}\n"
                f"Date : 15 Août 2026 — Conakry, Guinée\n\n"
                f"Veuillez trouver votre badge personnalisé en pièce jointe.\n"
                f"Imprimez-le et présentez-le à l'entrée de la conférence.\n\n"
                f"Cordialement,\n"
                f"L'équipe DounIA"
            ),
            from_email=admin_email,
            to=[inscrit.email],
        )
        email_participant.attach_file(pdf_path)
        email_participant.send(fail_silently=False)

        # Copie à l'organisateur
        email_admin = EmailMessage(
            subject=f"[Badge généré] {inscrit.prenom} {inscrit.nom} — {categorie_label}",
            body=(
                f"Badge généré et envoyé pour :\n\n"
                f"Nom : {inscrit.nom}\n"
                f"Prénoms : {inscrit.prenom}\n"
                f"Email : {inscrit.email}\n"
                f"Catégorie : {categorie_label}\n"
                f"Identifiant : {inscrit.identifiant}\n"
                f"Téléphone : {inscrit.telephone}\n"
                f"Organisation : {inscrit.organisation}\n"
            ),
            from_email=admin_email,
            to=[admin_email],
        )
        email_admin.attach_file(pdf_path)
        email_admin.send(fail_silently=False)

        messages.success(request,
            f"Inscription de {inscrit.prenom} {inscrit.nom} validée. "
            f"Badge généré et envoyé par email.")
    except Exception as e:
        messages.warning(request,
            f"Badge généré mais l'envoi email a échoué : {e}")

    return redirect('admin_conference_inscriptions')


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_conference_delete(request, pk):
    """Supprimer une inscription conférence."""
    inscrit = get_object_or_404(InscriptionConference, pk=pk)
    nom_complet = f"{inscrit.prenom} {inscrit.nom}"
    # Supprimer le fichier badge si existant
    if inscrit.badge_pdf:
        import os
        pdf_path = os.path.join(settings.MEDIA_ROOT, str(inscrit.badge_pdf))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    inscrit.delete()
    messages.success(request, f"Inscription de {nom_complet} supprimée.")
    return redirect('admin_conference_inscriptions')


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_conference_export_csv(request):
    """Export CSV des inscriptions conférence."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inscriptions_conference.csv"'
    response.write('\ufeff')  # BOM UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Identifiant', 'Nom', 'Prénoms', 'Email', 'Téléphone',
                     'Organisation', 'Catégorie', 'Date inscription', 'Validée'])

    for i in InscriptionConference.objects.all():
        writer.writerow([
            i.identifiant, i.nom, i.prenom, i.email, i.telephone,
            i.organisation, i.get_categorie_display(),
            i.date_inscription.strftime('%d/%m/%Y %H:%M'),
            'Oui' if i.valide else 'Non',
        ])

    return response


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_badge_template_upload(request):
    """Upload ou mise à jour d'un template de badge pour une catégorie."""
    if request.method == 'POST':
        categorie = request.POST.get('categorie', '')
        image = request.FILES.get('template_image')
        if not categorie or not image:
            messages.error(request, "Veuillez sélectionner une catégorie et un fichier image.")
            return redirect('admin_conference_inscriptions')

        badge_tpl, created = BadgeTemplate.objects.get_or_create(
            categorie=categorie,
            defaults={'template_image': image}
        )
        if not created:
            import os
            old_path = badge_tpl.template_image.path
            if os.path.exists(old_path):
                os.remove(old_path)
            badge_tpl.template_image = image
            badge_tpl.save()

        # Mettre à jour les coordonnées si fournies
        fields_int = ['nom_x', 'nom_y', 'nom_font_size', 'prenom_x', 'prenom_y',
                       'prenom_font_size', 'qr_x1', 'qr_y1', 'qr_x2', 'qr_y2']
        fields_str = ['nom_color', 'prenom_color']
        for f in fields_int:
            val = request.POST.get(f, '').strip()
            if val:
                try:
                    setattr(badge_tpl, f, int(val))
                except ValueError:
                    pass
        for f in fields_str:
            val = request.POST.get(f, '').strip()
            if val:
                setattr(badge_tpl, f, val)
        badge_tpl.save()

        label = dict(BadgeTemplate.CATEGORIE_CHOICES).get(categorie, categorie)
        messages.success(request, f"Template de badge '{label}' {'créé' if created else 'mis à jour'}.")

    return redirect('admin_conference_inscriptions')


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_badge_template_delete(request, pk):
    """Supprimer un template de badge."""
    tpl = get_object_or_404(BadgeTemplate, pk=pk)
    label = tpl.get_categorie_display()
    if tpl.template_image:
        import os
        path = tpl.template_image.path
        if os.path.exists(path):
            os.remove(path)
    tpl.delete()
    messages.success(request, f"Template '{label}' supprimé.")
    return redirect('admin_conference_inscriptions')


@user_passes_test(is_staff_user, login_url='/gestion/login/')
def admin_conference_export_badges_zip(request):
    """Télécharger tous les badges PDF générés dans un fichier ZIP."""
    import os
    import zipfile
    from io import BytesIO

    inscrits = InscriptionConference.objects.filter(valide=True).exclude(badge_pdf='').exclude(badge_pdf=None)

    if not inscrits.exists():
        messages.warning(request, "Aucun badge généré à exporter.")
        return redirect('admin_conference_inscriptions')

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for inscrit in inscrits:
            pdf_path = os.path.join(settings.MEDIA_ROOT, str(inscrit.badge_pdf))
            if os.path.exists(pdf_path):
                cat = inscrit.get_categorie_display().replace(' ', '_')
                filename = f"{cat}/badge_{inscrit.nom}_{inscrit.prenom}_{inscrit.identifiant}.pdf"
                zf.write(pdf_path, filename)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="badges_conference_dounia.zip"'
    return response
