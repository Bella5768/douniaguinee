from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .forms import InscriptionForm
from .models import Inscription, SiteConfiguration, ChiffreCle, Expert, Partenaire, HeroCarouselImage, HeroImage, StatsImage
import csv
from collections import OrderedDict
from django.utils import timezone
from django.core.mail import EmailMessage
from .pdf_agenda import generer_agenda_pdf


def is_staff_user(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff_user)
def manage_hero_stats_images(request):
    """Vue pour gérer les images du hero et des statistiques"""
    hero_images_gauche = HeroImage.objects.filter(position='gauche', active=True).order_by('ordre', 'date_ajout')
    hero_images_arriere = HeroImage.objects.filter(position='arriere', active=True).order_by('ordre', 'date_ajout')
    stats_images = StatsImage.objects.filter(active=True).order_by('ordre', 'date_ajout')
    
    context = {
        'hero_images_gauche': hero_images_gauche,
        'hero_images_arriere': hero_images_arriere,
        'stats_images': stats_images,
    }
    return render(request, 'inscriptions/manage_hero_stats_images.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_POST
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


@login_required
@user_passes_test(is_staff_user)
@require_POST
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


@login_required
@user_passes_test(is_staff_user)
@require_POST
def toggle_hero_image(request, image_id):
    """Activer/désactiver une image hero"""
    image = get_object_or_404(HeroImage, id=image_id)
    image.active = not image.active
    image.save()
    
    status = "activée" if image.active else "désactivée"
    return JsonResponse({'success': True, 'status': status})


@login_required
@user_passes_test(is_staff_user)
@require_POST
def toggle_stats_image(request, image_id):
    """Activer/désactiver une image statistiques"""
    image = get_object_or_404(StatsImage, id=image_id)
    image.active = not image.active
    image.save()
    
    status = "activée" if image.active else "désactivée"
    return JsonResponse({'success': True, 'status': status})


@login_required
@user_passes_test(is_staff_user)
@require_POST
def delete_hero_image(request, image_id):
    """Supprimer une image hero"""
    image = get_object_or_404(HeroImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_staff_user)
@require_POST
def delete_stats_image(request, image_id):
    """Supprimer une image statistiques"""
    image = get_object_or_404(StatsImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_staff_user)
@require_POST
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


@login_required
@user_passes_test(is_staff_user)
@require_POST
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


def landing_page(request):
    form = InscriptionForm()
    atelier_param = request.GET.get('atelier', '')
    if atelier_param:
        form = InscriptionForm(initial={'atelier': atelier_param})

    config = SiteConfiguration.get()
    chiffres = ChiffreCle.objects.all().order_by('ordre')
    experts = Expert.objects.all().order_by('ordre')
    partenaires = Partenaire.objects.all().order_by('ordre')
    hero_images = HeroCarouselImage.objects.filter(active=True).order_by('ordre', 'date_ajout')

    context = {
        'form': form,
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'partenaires': partenaires,
        'hero_images': hero_images,
    }
    return render(request, 'inscriptions/landing.html', context)

    # Parse multiline fields
    defis = [d.strip() for d in config.dounia1_defis.split('\n') if d.strip()]
    opportunites = [o.strip() for o in config.dounia1_opportunites.split('\n') if o.strip()]
    rapport_points = [p.strip() for p in config.rapport_points.split('\n') if p.strip()]

    # Parse phases (titre|description)
    phases = []
    for p in [config.dounia2_phase1, config.dounia2_phase2, config.dounia2_phase3, config.dounia2_phase4]:
        parts = p.split('|', 1)
        phases.append({'titre': parts[0].strip(), 'description': parts[1].strip() if len(parts) > 1 else ''})

    context = {
        'form': form,
        'ateliers': Inscription.ATELIER_CHOICES,
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'partenaires': partenaires,
        'hero_images': hero_images,
        'defis': defis,
        'opportunites': opportunites,
        'rapport_points': rapport_points,
        'phases': phases,
    }
    return render(request, 'inscriptions/landing.html', context)


def inscription_submit(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            inscription = form.save()
            # Send confirmation email
            try:
                send_mail(
                    subject='Confirmation d\'inscription — DounIA 2',
                    message=(
                        f"Bonjour {inscription.prenom} {inscription.nom},\n\n"
                        f"Votre inscription à l'atelier « {inscription.get_atelier_display()} » "
                        f"a bien été enregistrée.\n\n"
                        f"Détails de votre inscription :\n"
                        f"- Profil : {inscription.get_profil_display()}\n"
                        f"- Institution : {inscription.institution}\n"
                        f"- Format : {inscription.get_format_preference_display()}\n"
                        f"- Engagement : {inscription.get_engagement_display()}\n\n"
                        f"Nous vous contacterons prochainement avec les détails "
                        f"pratiques de votre atelier.\n\n"
                        f"Merci pour votre engagement,\n"
                        f"L'équipe DounIA"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[inscription.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            return redirect('inscription_confirmation')
        else:
            context = {
                'form': form,
                'ateliers': Inscription.ATELIER_CHOICES,
            }
            return render(request, 'inscriptions/landing.html', context)
    return redirect('landing_page')


def inscription_confirmation(request):
    return render(request, 'inscriptions/confirmation.html')


def export_inscriptions_csv(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inscriptions_dounia.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Date', 'Nom', 'Prénom', 'Email', 'WhatsApp',
        'Institution', 'Fonction', 'Profil', 'Atelier',
        'Engagement', 'Format', 'Disponibilité', 'Motivation'
    ])

    inscriptions = Inscription.objects.all()
    for insc in inscriptions:
        writer.writerow([
            insc.date_inscription.strftime('%d/%m/%Y %H:%M'),
            insc.nom, insc.prenom, insc.email, insc.whatsapp,
            insc.institution, insc.fonction,
            insc.get_profil_display(), insc.get_atelier_display(),
            insc.get_engagement_display(), insc.get_format_preference_display(),
            insc.get_disponibilite_display(), insc.motivation,
        ])

    return response


# ============ ADMIN DASHBOARD VIEWS ============

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', 'admin_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Identifiants invalides ou accès non autorisé.')
    return render(request, 'gestion/login.html')


def admin_logout(request):
    logout(request)
    return redirect('landing_page')


@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    total = Inscription.objects.count()
    stats_atelier = Inscription.objects.values('atelier').annotate(count=Count('id')).order_by('-count')
    stats_profil = Inscription.objects.values('profil').annotate(count=Count('id')).order_by('-count')
    stats_format = Inscription.objects.values('format_preference').annotate(count=Count('id')).order_by('-count')
    stats_engagement = Inscription.objects.values('engagement').annotate(count=Count('id')).order_by('-count')
    recent = Inscription.objects.order_by('-date_inscription')[:10]

    atelier_labels = dict(Inscription.ATELIER_CHOICES)
    profil_labels = dict(Inscription.PROFIL_CHOICES)
    format_labels = dict(Inscription.FORMAT_CHOICES)
    engagement_labels = dict(Inscription.ENGAGEMENT_CHOICES)

    for s in stats_atelier:
        s['label'] = atelier_labels.get(s['atelier'], s['atelier'])
    for s in stats_profil:
        s['label'] = profil_labels.get(s['profil'], s['profil'])
    for s in stats_format:
        s['label'] = format_labels.get(s['format_preference'], s['format_preference'])
    for s in stats_engagement:
        s['label'] = engagement_labels.get(s['engagement'], s['engagement'])

    context = {
        'total': total,
        'stats_atelier': stats_atelier,
        'stats_profil': stats_profil,
        'stats_format': stats_format,
        'stats_engagement': stats_engagement,
        'recent': recent,
    }
    return render(request, 'gestion/dashboard.html', context)


@login_required(login_url='admin_login')
def admin_inscriptions(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    qs = Inscription.objects.all()

    # Filters
    atelier = request.GET.get('atelier', '')
    profil = request.GET.get('profil', '')
    engagement = request.GET.get('engagement', '')
    format_pref = request.GET.get('format', '')
    search = request.GET.get('q', '')

    if atelier:
        qs = qs.filter(atelier=atelier)
    if profil:
        qs = qs.filter(profil=profil)
    if engagement:
        qs = qs.filter(engagement=engagement)
    if format_pref:
        qs = qs.filter(format_preference=format_pref)
    if search:
        qs = qs.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search) |
            Q(institution__icontains=search)
        )

    context = {
        'inscriptions': qs,
        'total': qs.count(),
        'atelier_choices': Inscription.ATELIER_CHOICES,
        'profil_choices': Inscription.PROFIL_CHOICES,
        'engagement_choices': Inscription.ENGAGEMENT_CHOICES,
        'format_choices': Inscription.FORMAT_CHOICES,
        'current_atelier': atelier,
        'current_profil': profil,
        'current_engagement': engagement,
        'current_format': format_pref,
        'current_search': search,
    }
    return render(request, 'gestion/inscriptions.html', context)


@login_required(login_url='admin_login')
def admin_inscription_detail(request, pk):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    inscription = get_object_or_404(Inscription, pk=pk)
    return render(request, 'gestion/detail.html', {'inscription': inscription})


@login_required(login_url='admin_login')
def admin_inscription_edit(request, pk):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inscription de {inscription.prenom} {inscription.nom} mise à jour.')
            return redirect('admin_inscription_detail', pk=pk)
    else:
        form = InscriptionForm(instance=inscription)

    return render(request, 'gestion/edit.html', {'form': form, 'inscription': inscription})


@login_required(login_url='admin_login')
def admin_inscription_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        nom_complet = f'{inscription.prenom} {inscription.nom}'
        inscription.delete()
        messages.success(request, f'Inscription de {nom_complet} supprimée.')
        return redirect('admin_inscriptions')

    return render(request, 'gestion/delete.html', {'inscription': inscription})


@login_required(login_url='admin_login')
def admin_inscription_valider(request, pk):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    inscription = get_object_or_404(Inscription, pk=pk)

    if request.method == 'POST':
        if inscription.valide:
            messages.info(request, f'L\'inscription de {inscription.prenom} {inscription.nom} est déjà validée.')
            return redirect('admin_inscription_detail', pk=pk)

        pdf_file = request.FILES.get('agenda_pdf')
        if not pdf_file:
            messages.error(request, 'Veuillez joindre le fichier PDF de l\'agenda avant de valider.')
            return redirect('admin_inscription_detail', pk=pk)

        if not pdf_file.name.lower().endswith('.pdf'):
            messages.error(request, 'Le fichier doit être au format PDF.')
            return redirect('admin_inscription_detail', pk=pk)

        inscription.valide = True
        inscription.date_validation = timezone.now()
        inscription.save()

        # Choix du serveur SMTP
        provider = request.POST.get('email_provider', settings.DEFAULT_EMAIL_PROVIDER)
        if provider == 'outlook':
            smtp_host = settings.OUTLOOK_HOST
            smtp_port = settings.OUTLOOK_PORT
            smtp_user = settings.OUTLOOK_USER
            smtp_password = settings.OUTLOOK_PASSWORD
        else:
            smtp_host = settings.GMAIL_HOST
            smtp_port = settings.GMAIL_PORT
            smtp_user = settings.GMAIL_USER
            smtp_password = settings.GMAIL_PASSWORD

        from_email = smtp_user
        provider_label = 'Gmail' if provider == 'gmail' else 'Outlook'

        try:
            from django.core.mail import get_connection
            connection = get_connection(
                host=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=True,
            )

            email = EmailMessage(
                subject='Inscription validée + Agenda de votre atelier — DounIA 2',
                body=(
                    f"Bonjour {inscription.prenom} {inscription.nom},\n\n"
                    f"Nous avons le plaisir de vous confirmer que votre inscription "
                    f"à l'atelier « {inscription.get_atelier_display()} » a été validée "
                    f"par l'équipe DounIA.\n\n"
                    f"Vous trouverez en pièce jointe l'agenda de votre atelier.\n\n"
                    f"Récapitulatif de votre inscription :\n"
                    f"- Profil : {inscription.get_profil_display()}\n"
                    f"- Institution : {inscription.institution}\n"
                    f"- Fonction : {inscription.fonction}\n"
                    f"- Format préféré : {inscription.get_format_preference_display()}\n"
                    f"- Engagement : {inscription.get_engagement_display()}\n"
                    f"- Disponibilité : {inscription.get_disponibilite_display()}\n\n"
                    f"Merci pour votre engagement au service de la Guinée.\n\n"
                    f"Cordialement,\n"
                    f"L'équipe DounIA\n"
                    f"contact@dounia.gn"
                ),
                from_email=from_email,
                to=[inscription.email],
                connection=connection,
            )

            email.attach(pdf_file.name, pdf_file.read(), 'application/pdf')
            email.send(fail_silently=False)
            messages.success(request, f'Inscription de {inscription.prenom} {inscription.nom} validée. Email + PDF envoyés via {provider_label} à {inscription.email}.')
        except Exception as e:
            messages.warning(request, f'Inscription validée, mais l\'email n\'a pas pu être envoyé via {provider_label} : {e}')

        return redirect('admin_inscription_detail', pk=pk)

    return redirect('admin_inscription_detail', pk=pk)


# ============ ADMIN PAGE CONTENT VIEWS ============

@login_required(login_url='admin_login')
def admin_contenu_page(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)
    config = SiteConfiguration.get()
    chiffres = ChiffreCle.objects.all()
    experts_list = Expert.objects.all()
    partenaires_list = Partenaire.objects.all()
    context = {
        'config': config,
        'chiffres': chiffres,
        'experts_list': experts_list,
        'partenaires_list': partenaires_list,
    }
    return render(request, 'gestion/contenu_page.html', context)


@login_required(login_url='admin_login')
def admin_edit_section(request, section):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    config = SiteConfiguration.get()
    SECTIONS = {
        'hero': {
            'titre': 'Section Hero',
            'fields': ['hero_badge', 'hero_titre', 'hero_description', 'hero_image', 'hero_image_url',
                        'hero_btn1_texte', 'hero_btn1_lien', 'hero_btn2_texte', 'hero_btn2_lien'],
        },
        'about': {
            'titre': 'Section À propos',
            'fields': ['about_titre', 'about_sous_titre',
                        'about_card1_icone', 'about_card1_titre', 'about_card1_texte',
                        'about_card2_icone', 'about_card2_titre', 'about_card2_texte',
                        'about_card3_icone', 'about_card3_titre', 'about_card3_texte'],
        },
        'dounia1': {
            'titre': 'Section DounIA 1',
            'fields': ['dounia1_titre', 'dounia1_sous_titre', 'dounia1_defis', 'dounia1_opportunites'],
        },
        'rapport': {
            'titre': 'Section Rapport',
            'fields': ['rapport_titre', 'rapport_sous_titre', 'rapport_description', 'rapport_points', 'rapport_lien'],
        },
        'podcast': {
            'titre': 'Section Podcast',
            'fields': ['podcast_titre', 'podcast_description', 'podcast_lien'],
        },
        'dounia2': {
            'titre': 'Section DounIA 2',
            'fields': ['dounia2_badge', 'dounia2_titre', 'dounia2_description',
                        'dounia2_phase1', 'dounia2_phase2', 'dounia2_phase3', 'dounia2_phase4'],
        },
        'inscription_section': {
            'titre': 'Section Inscription',
            'fields': ['inscription_titre', 'inscription_sous_titre'],
        },
        'footer': {
            'titre': 'Footer',
            'fields': ['footer_description', 'footer_email', 'footer_lieu'],
        },
    }

    if section not in SECTIONS:
        return redirect('admin_contenu_page')

    section_info = SECTIONS[section]

    if request.method == 'POST':
        for field_name in section_info['fields']:
            field = SiteConfiguration._meta.get_field(field_name)
            if isinstance(field, models.ImageField):
                if request.FILES.get(field_name):
                    setattr(config, field_name, request.FILES[field_name])
            else:
                value = request.POST.get(field_name, '')
                setattr(config, field_name, value)
        config.save()
        messages.success(request, f'{section_info["titre"]} mise à jour avec succès.')
        return redirect('admin_contenu_page')

    fields_data = []
    for field_name in section_info['fields']:
        field = SiteConfiguration._meta.get_field(field_name)
        fields_data.append({
            'name': field_name,
            'label': field.verbose_name,
            'value': getattr(config, field_name),
            'help_text': getattr(field, 'help_text', ''),
            'is_textarea': isinstance(field, models.TextField),
            'is_url': isinstance(field, models.URLField),
            'is_image': isinstance(field, models.ImageField),
        })

    context = {
        'section': section,
        'section_titre': section_info['titre'],
        'fields_data': fields_data,
    }
    return render(request, 'gestion/edit_section.html', context)


@login_required(login_url='admin_login')
def admin_chiffres(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            ChiffreCle.objects.create(
                nombre=int(request.POST.get('nombre', 0)),
                suffixe=request.POST.get('suffixe', ''),
                label=request.POST.get('label', ''),
                ordre=int(request.POST.get('ordre', 0)),
            )
            messages.success(request, 'Chiffre clé ajouté.')
        elif action == 'delete':
            ChiffreCle.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Chiffre clé supprimé.')
        elif action == 'edit':
            obj = get_object_or_404(ChiffreCle, pk=request.POST.get('pk'))
            obj.nombre = int(request.POST.get('nombre', 0))
            obj.suffixe = request.POST.get('suffixe', '')
            obj.label = request.POST.get('label', '')
            obj.ordre = int(request.POST.get('ordre', 0))
            obj.save()
            messages.success(request, 'Chiffre clé modifié.')
        return redirect('admin_chiffres')
    chiffres = ChiffreCle.objects.all()
    return render(request, 'gestion/chiffres.html', {'chiffres': chiffres})


@login_required(login_url='admin_login')
def admin_experts(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            expert = Expert(
                nom=request.POST.get('nom', ''),
                specialite=request.POST.get('specialite', ''),
                ordre=int(request.POST.get('ordre', 0)),
            )
            if request.FILES.get('photo'):
                expert.photo = request.FILES['photo']
            expert.save()
            messages.success(request, 'Expert ajouté.')
        elif action == 'delete':
            Expert.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Expert supprimé.')
        elif action == 'edit':
            obj = get_object_or_404(Expert, pk=request.POST.get('pk'))
            obj.nom = request.POST.get('nom', '')
            obj.specialite = request.POST.get('specialite', '')
            obj.ordre = int(request.POST.get('ordre', 0))
            if request.FILES.get('photo'):
                obj.photo = request.FILES['photo']
            obj.save()
            messages.success(request, 'Expert modifié.')
        return redirect('admin_experts')
    experts_list = Expert.objects.all()
    return render(request, 'gestion/experts.html', {'experts_list': experts_list})


@login_required(login_url='admin_login')
def admin_partenaires(request):
    if not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            p = Partenaire(
                nom=request.POST.get('nom', ''),
                site_web=request.POST.get('site_web', ''),
                ordre=int(request.POST.get('ordre', 0)),
            )
            if request.FILES.get('logo'):
                p.logo = request.FILES['logo']
            p.save()
            messages.success(request, 'Partenaire ajouté.')
        elif action == 'delete':
            Partenaire.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Partenaire supprimé.')
        elif action == 'edit':
            obj = get_object_or_404(Partenaire, pk=request.POST.get('pk'))
            obj.nom = request.POST.get('nom', '')
            obj.site_web = request.POST.get('site_web', '')
            obj.ordre = int(request.POST.get('ordre', 0))
            if request.FILES.get('logo'):
                obj.logo = request.FILES['logo']
            obj.save()
            messages.success(request, 'Partenaire modifié.')
        return redirect('admin_partenaires')
    partenaires_list = Partenaire.objects.all()
    return render(request, 'gestion/partenaires.html', {'partenaires_list': partenaires_list})


def rapport_download(request):
    """Vue pour gérer le téléchargement du rapport après formulaire"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        institution = request.POST.get('institution', '').strip()
        usage = request.POST.get('usage', '').strip()
        consent = request.POST.get('consent') == 'on'
        
        # Validation basique
        if not all([nom, prenom, email, institution, usage]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('landing_page')
        
        # Ici vous pourriez sauvegarder ces données dans un modèle séparé
        # ou envoyer un email de notification
        
        # Envoyer le email de notification à l'admin
        try:
            sujet = f"Nouveau téléchargement du rapport - {nom} {prenom}"
            message = f"""
Nouveau téléchargement du rapport DounIA 1:

Nom: {nom} {prenom}
Email: {email}
Institution: {institution}
Objectif: {usage}
Consentement communications: {consent}
Date: {timezone.now().strftime('%d/%m/%Y %H:%M')}
            """
            send_mail(
                sujet,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Envoyer à l'admin
                fail_silently=True,
            )
        except Exception as e:
            pass


@login_required
@user_passes_test(is_staff_user)
def manage_hero_images(request):
    """Vue pour gérer les images du carousel hero (ancienne fonction)"""
    hero_images = HeroCarouselImage.objects.all().order_by('ordre', 'date_ajout')
    
    context = {
        'hero_images': hero_images,
    }
    return render(request, 'inscriptions/manage_hero_images.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_POST
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


def landing_page(request):
    form = InscriptionForm()
    atelier_param = request.GET.get('atelier', '')
    if atelier_param:
        form = InscriptionForm(initial={'atelier': atelier_param})

    config = SiteConfiguration.get()
    chiffres = ChiffreCle.objects.all().order_by('ordre')
    experts = Expert.objects.all().order_by('ordre')
    partenaires = Partenaire.objects.all().order_by('ordre')
    hero_images = HeroCarouselImage.objects.filter(active=True).order_by('ordre', 'date_ajout')

    context = {
        'form': form,
        'config': config,
        'chiffres': chiffres,
        'experts': experts,
        'partenaires': partenaires,
        'hero_images': hero_images,
    }
    return render(request, 'inscriptions/landing.html', context)
