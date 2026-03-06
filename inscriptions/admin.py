from django.contrib import admin
from .models import (
    Inscription, SiteConfiguration, Expert, Partenaire, ChiffreCle, 
    HeroCarouselImage, HeroImage, StatsImage, EvenementImage, RestitutionImage,
    DouniaEvent, Restitution, Atelier
)


class _BaseEvenementImageInline(admin.TabularInline):
    model = EvenementImage
    extra = 0
    fields = ('titre', 'image', 'image_url', 'description', 'ordre', 'active')
    ordering = ('ordre', 'date_ajout')


class EvenementHeroImageInline(_BaseEvenementImageInline):
    verbose_name = "Image Hero"
    verbose_name_plural = "Images Hero (arrière-plan)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(position='hero')


class EvenementGalerieImageInline(_BaseEvenementImageInline):
    verbose_name = "Image Galerie"
    verbose_name_plural = "Images Galerie"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(position='galerie')

    def save_new_objects(self, formset, commit=True):
        # Ensure default position when adding from this inline
        for obj in formset.new_objects:
            if not obj.position:
                obj.position = 'galerie'
        return super().save_new_objects(formset, commit=commit)


class _BaseRestitutionImageInline(admin.TabularInline):
    model = RestitutionImage
    extra = 0
    fields = ('titre', 'image', 'image_url', 'description', 'ordre', 'active')
    ordering = ('ordre', 'date_ajout')


class RestitutionHeroImageInline(_BaseRestitutionImageInline):
    verbose_name = "Image Hero"
    verbose_name_plural = "Images Hero (arrière-plan)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(position='hero')


class RestitutionGalerieImageInline(_BaseRestitutionImageInline):
    verbose_name = "Image Galerie"
    verbose_name_plural = "Images Galerie"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(position='galerie')

    def save_new_objects(self, formset, commit=True):
        for obj in formset.new_objects:
            if not obj.position:
                obj.position = 'galerie'
        return super().save_new_objects(formset, commit=commit)


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'position', 'ordre', 'active', 'date_ajout')
    list_filter = ('position', 'active', 'date_ajout')
    search_fields = ('titre',)
    list_editable = ('ordre', 'active')
    readonly_fields = ('date_ajout',)
    ordering = ('position', 'ordre', 'date_ajout')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(StatsImage)
class StatsImageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ordre', 'active', 'date_ajout')
    list_filter = ('active', 'date_ajout')
    search_fields = ('titre',)
    list_editable = ('ordre', 'active')
    readonly_fields = ('date_ajout',)
    ordering = ('ordre', 'date_ajout')
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'prenom', 'email', 'institution',
        'atelier', 'profil', 'date_inscription',
    ]
    list_filter = ['atelier', 'profil', 'engagement', 'format_preference', 'disponibilite']
    search_fields = ['nom', 'prenom', 'email', 'institution']
    readonly_fields = ['date_inscription']
    ordering = ['-date_inscription']

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inscriptions_dounia.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Date', 'Nom', 'Prénom', 'Email', 'WhatsApp',
            'Institution', 'Fonction', 'Profil', 'Atelier',
            'Engagement', 'Format', 'Disponibilité', 'Motivation'
        ])

        for insc in queryset:
            writer.writerow([
                insc.date_inscription.strftime('%d/%m/%Y %H:%M'),
                insc.nom, insc.prenom, insc.email, insc.whatsapp,
                insc.institution, insc.fonction,
                insc.get_profil_display(), insc.get_atelier_display(),
                insc.get_engagement_display(), insc.get_format_preference_display(),
                insc.get_disponibilite_display(), insc.motivation,
            ])

        return response

    export_as_csv.short_description = 'Exporter en CSV'


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ['nom', 'specialite', 'ordre', 'photo_preview']
    list_filter = ['specialite']
    search_fields = ['nom', 'specialite']
    list_editable = ['ordre']
    ordering = ['ordre', 'nom']

    def photo_preview(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius:50%; object-fit:cover;">'
        return "Pas de photo"
    photo_preview.allow_tags = True
    photo_preview.short_description = 'Aperçu'


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'logo_preview', 'site_web', 'ordre']
    search_fields = ['nom']
    list_editable = ['ordre']
    ordering = ['ordre', 'nom']

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" width="50" height="30" style="object-fit:contain;">'
        return "Pas de logo"
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Aperçu'


@admin.register(HeroCarouselImage)
class HeroCarouselImageAdmin(admin.ModelAdmin):
    list_display = ['titre', 'image_preview', 'ordre', 'active', 'date_ajout']
    list_filter = ['active', 'date_ajout']
    search_fields = ['titre']
    list_editable = ['ordre', 'active']
    ordering = ['ordre', 'date_ajout']
    readonly_fields = ['date_ajout']

    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'ordre', 'active')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Uploader une image OU fournir une URL. L\'image uploadée a priorité.'
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        url = obj.get_image_url()
        return f'<img src="{url}" width="80" height="60" style="border-radius:8px; object-fit:cover;">'
    image_preview.allow_tags = True
    image_preview.short_description = 'Aperçu'


@admin.register(EvenementImage)
class EvenementImageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'evenement', 'ordre', 'active', 'date_ajout')
    list_filter = ('evenement', 'active', 'date_ajout')
    search_fields = ('titre', 'description')
    list_editable = ('ordre', 'active')
    ordering = ('evenement', 'ordre', 'date_ajout')
    readonly_fields = ('date_ajout',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('evenement', 'titre', 'description', 'ordre', 'active')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Uploader une image OU fournir une URL. L\'image uploadée a priorité.'
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        url = obj.get_image_url()
        return f'<img src="{url}" width="80" height="60" style="border-radius:8px; object-fit:cover;">'
    image_preview.allow_tags = True
    image_preview.short_description = 'Aperçu'


@admin.register(RestitutionImage)
class RestitutionImageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ordre', 'active', 'date_ajout')
    list_filter = ('active', 'date_ajout')
    search_fields = ('titre', 'description')
    list_editable = ('ordre', 'active')
    ordering = ('ordre', 'date_ajout')
    readonly_fields = ('date_ajout',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'ordre', 'active')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Uploader une image OU fournir une URL. L\'image uploadée a priorité.'
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        url = obj.get_image_url()
        return f'<img src="{url}" width="80" height="60" style="border-radius:8px; object-fit:cover;">'
    image_preview.allow_tags = True
    image_preview.short_description = 'Aperçu'


@admin.register(DouniaEvent)
class DouniaEventAdmin(admin.ModelAdmin):
    list_display = ('event_slug', 'titre_hero', 'actif', 'created_at')
    list_filter = ('event_slug', 'actif', 'created_at')
    search_fields = ('titre_hero', 'description_hero')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('event_slug', '-created_at')

    inlines = (EvenementHeroImageInline, EvenementGalerieImageInline)

    fieldsets = (
        ('Informations générales', {
            'fields': ('event_slug', 'titre_hero', 'description_hero', 'actif')
        }),
        ('Section Hero', {
            'fields': ('hero_image', 'hero_image_url', 'bouton_principal_texte', 'bouton_principal_lien', 'bouton_secondaire_texte', 'bouton_secondaire_lien')
        }),
        ('Section Objectifs', {
            'fields': ('objectifs_titre', 'objectifs_description', 'objectifs_points'),
            'classes': ('collapse',)
        }),
        ('Section Chiffres clés', {
            'fields': ('chiffres_titre', 'chiffres_image', 'chiffres_image_url', 'chiffres'),
            'classes': ('collapse',)
        }),
        ('Section Programme', {
            'fields': ('programme_titre', 'programme_description', 'programme_sessions'),
            'classes': ('collapse',)
        }),
        ('Section Partenaires', {
            'fields': ('partenaires_titre', 'partenaires_description'),
            'classes': ('collapse',)
        }),
        ('Section Inscription', {
            'fields': ('inscription_titre', 'inscription_description', 'inscription_date_limite', 'inscription_lieu'),
            'classes': ('collapse',)
        }),
        ('Section Contact', {
            'fields': ('contact_titre', 'contact_email', 'contact_telephone', 'contact_adresse'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Restitution)
class RestitutionAdmin(admin.ModelAdmin):
    list_display = ('titre_hero', 'created_at')
    search_fields = ('titre_hero', 'description_hero')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    inlines = (RestitutionHeroImageInline, RestitutionGalerieImageInline)

    fieldsets = (
        ('Section Hero', {
            'fields': ('titre_hero', 'description_hero', 'hero_image', 'hero_image_url')
        }),
        ('Cérémonie', {
            'fields': (
                'section_titre',
                'contexte_titre', 'contexte_texte', 'contexte_points',
                'objectif_titre', 'objectif_general', 'objectifs_specifiques',
                'resultats_titre', 'resultats_intro', 'resultats_attendus',
                'public_titre_ceremonie', 'public_cible',
            ),
        }),
        ('Agenda', {
            'fields': (
                'agenda_label_duree', 'agenda_label_date', 'agenda_label_invites',
                'agenda_titre', 'agenda_date', 'agenda_duree', 'agenda_invites', 'agenda_sessions',
                'agenda_empty_message',
            ),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Atelier)
class AtelierAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'ordre', 'active', 'image_preview')
    list_filter = ('active',)
    search_fields = ('code', 'label', 'description')
    list_editable = ('ordre', 'active')
    ordering = ('ordre', 'label')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'label', 'description', 'ordre', 'active')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'classes': ('collapse',)
        }),
        ('Détails pour la page "À propos"', {
            'fields': ('contexte', 'objectif', 'questions_cles', 'intervenants', 'lien_inscription'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        url = obj.get_image_url()
        if url:
            return f'<img src="{url}" width="50" height="50" style="border-radius:8px; object-fit:cover;">'
        return "Pas d'image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Aperçu'


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('hero_titre', 'hero_badge', 'hero_image_preview')
    search_fields = ('hero_titre', 'hero_description')
    readonly_fields = ('id',)

    fieldsets = (
        ('Hero Section', {
            'fields': (
                'hero_badge', 'hero_titre', 'hero_titre_span', 'hero_description',
                'hero_image', 'hero_image_url',
                'hero_btn1_texte', 'hero_btn1_lien', 'hero_btn2_texte', 'hero_btn2_lien'
            )
        }),
        ('About Section', {
            'fields': (
                'about_titre', 'about_sous_titre',
                'about_card1_icone', 'about_card1_titre', 'about_card1_texte',
                'about_card2_icone', 'about_card2_titre', 'about_card2_texte',
                'about_card3_icone', 'about_card3_titre', 'about_card3_texte'
            ),
            'classes': ('collapse',)
        }),
        ('DounIA 1', {
            'fields': (
                'dounia1_titre', 'dounia1_sous_titre', 'dounia1_defis', 'dounia1_opportunites'
            ),
            'classes': ('collapse',)
        }),
        ('Rapport', {
            'fields': (
                'rapport_titre', 'rapport_sous_titre', 'rapport_description',
                'rapport_points', 'rapport_lien', 'rapport_fichier', 'rapport_image'
            ),
            'classes': ('collapse',)
        }),
        ('Podcast', {
            'fields': (
                'podcast_titre', 'podcast_description', 'podcast_lien', 'podcast_fichier'
            ),
            'classes': ('collapse',)
        }),
        ('DounIA 2', {
            'fields': (
                'dounia2_badge', 'dounia2_titre', 'dounia2_description',
                'dounia2_phase1', 'dounia2_phase2', 'dounia2_phase3', 'dounia2_phase4'
            ),
            'classes': ('collapse',)
        }),
        ('Video', {
            'fields': (
                'video_titre', 'video_sous_titre', 'video_lien', 'video_fichier'
            ),
            'classes': ('collapse',)
        }),
        ('Inscription', {
            'fields': (
                'inscription_titre', 'inscription_sous_titre'
            ),
            'classes': ('collapse',)
        }),
        ('Porteurs', {
            'fields': (
                'porteur1_nom', 'porteur1_description', 'porteur1_logo',
                'porteur2_nom', 'porteur2_description', 'porteur2_logo'
            ),
            'classes': ('collapse',)
        }),
        ('Footer', {
            'fields': (
                'footer_description', 'footer_email', 'footer_lieu'
            ),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )

    def hero_image_preview(self, obj):
        if obj.hero_image:
            return f'<img src="{obj.hero_image.url}" width="80" height="60" style="border-radius:8px; object-fit:cover;">'
        elif obj.hero_image_url:
            return f'<img src="{obj.hero_image_url}" width="80" height="60" style="border-radius:8px; object-fit:cover;">'
        return "Pas d'image"
    hero_image_preview.allow_tags = True
    hero_image_preview.short_description = 'Image Hero'

    def has_add_permission(self, request):
        # Limiter à une seule configuration
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
