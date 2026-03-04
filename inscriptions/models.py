from django.db import models
from django.core.validators import URLValidator
import os
from django.utils import timezone


class HeroImage(models.Model):
    """Images du hero (gauche et arrière-plan)"""
    titre = models.CharField(max_length=100, verbose_name='Titre')
    image = models.ImageField(upload_to='hero_images/', blank=True, null=True, verbose_name='Image uploadée')
    image_url = models.URLField(max_length=500, blank=True, verbose_name='URL de l\'image')
    position = models.CharField(
        max_length=20,
        choices=[
            ('gauche', 'Gauche (carousel)'),
            ('arriere', 'Arrière-plan (défilant)'),
        ],
        default='gauche',
        verbose_name='Position'
    )
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    active = models.BooleanField(default=True, verbose_name='Active')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')

    class Meta:
        verbose_name = 'Image Hero'
        verbose_name_plural = 'Images Hero'
        ordering = ['position', 'ordre', 'date_ajout']

    def __str__(self):
        return f"{self.titre} ({self.get_position_display()})"

    def get_image_url(self):
        """Retourne l'URL de l'image avec priorité à l'image uploadée"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80'

    def get_position_display(self):
        return dict(self._meta.get_field('position').choices).get(self.position, self.position)


class StatsImage(models.Model):
    """Images des statistiques (arrière-plan défilant)"""
    titre = models.CharField(max_length=100, verbose_name='Titre')
    image = models.ImageField(upload_to='stats_images/', blank=True, null=True, verbose_name='Image uploadée')
    image_url = models.URLField(max_length=500, blank=True, verbose_name='URL de l\'image')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    active = models.BooleanField(default=True, verbose_name='Active')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')

    class Meta:
        verbose_name = 'Image Statistiques'
        verbose_name_plural = 'Images Statistiques'
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return self.titre

    def get_image_url(self):
        """Retourne l'URL de l'image avec priorité à l'image uploadée"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80'


class DouniaEvent(models.Model):
    """Modèle pour les pages d'événements DounIA"""
    EVENT_CHOICES = [
        ('dounia1', 'DounIA 1'),
        ('dounia2', 'DounIA 2'),
    ]
    
    event_slug = models.CharField(max_length=20, choices=EVENT_CHOICES, unique=True)
    
    # Section Hero
    titre_hero = models.CharField(max_length=200)
    description_hero = models.TextField()
    hero_image = models.ImageField(upload_to='evenements/hero/', blank=True, null=True, verbose_name='Image Hero (upload)')
    hero_image_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Image Hero URL (fallback)')
    bouton_principal_texte = models.CharField(max_length=100, default="S'inscrire")
    bouton_principal_lien = models.CharField(max_length=200, default="#inscription")
    bouton_secondaire_texte = models.CharField(max_length=100, default="En savoir plus")
    bouton_secondaire_lien = models.CharField(max_length=200, default="#")
    
    # Section Objectifs
    objectifs_titre = models.CharField(max_length=200, default="Objectifs")
    objectifs_description = models.TextField()
    objectifs_points = models.JSONField(default=list, blank=True, help_text="Liste des objectifs")
    
    # Section Chiffres clés
    chiffres_titre = models.CharField(max_length=200, default="Chiffres clés")
    chiffres = models.JSONField(default=list, blank=True, help_text="Liste des chiffres avec nombre et label")
    chiffres_image = models.ImageField(upload_to='evenements/chiffres/', blank=True, null=True, verbose_name='Image Statistiques (upload)')
    chiffres_image_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Image Statistiques URL (fallback)')
    
    # Section Programme
    programme_titre = models.CharField(max_length=200, default="Programme")
    programme_description = models.TextField()
    programme_sessions = models.JSONField(default=list, blank=True, help_text="Liste des sessions avec heure, titre et description")
    
    # Section Partenaires
    partenaires_titre = models.CharField(max_length=200, default="Partenaires")
    partenaires_description = models.TextField(default="")
    
    # Section Inscription
    inscription_titre = models.CharField(max_length=200, default="Inscription")
    inscription_description = models.TextField()
    inscription_date_limite = models.DateField(null=True, blank=True)
    inscription_lieu = models.CharField(max_length=200, blank=True)
    
    # Section Contact
    contact_titre = models.CharField(max_length=200, default="Contact")
    contact_email = models.EmailField(blank=True)
    contact_telephone = models.CharField(max_length=20, blank=True)
    contact_adresse = models.TextField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    # État
    actif = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Événement DounIA"
        verbose_name_plural = "Événements DounIA"
    
    def __str__(self):
        return f"{self.get_event_slug_display()} - {self.titre_hero}"
    
    def get_meta_title(self):
        return self.meta_title or f"{self.titre_hero} - DounIA"


class Restitution(models.Model):
    """Modèle pour la page de restitution"""
    titre_hero = models.CharField(max_length=200, default="Restitution DounIA")
    description_hero = models.TextField(default="Découvrez les résultats, recommandations et conclusions des ateliers de concertation sur la gouvernance des données et l'intelligence artificielle en Guinée.")
    hero_image = models.ImageField(upload_to='restitution/hero/', blank=True, null=True, verbose_name='Image Hero (upload)')
    hero_image_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Image Hero URL (fallback)')

    contexte_titre = models.CharField(max_length=200, default="Contexte et justification")
    contexte_texte = models.TextField(default=(
        "L’Afrique entre progressivement dans l’ère du numérique, des données et de l’intelligence artificielle (IA). Toutefois, le continent demeure encore largement en position de consommateur de technologies conçues ailleurs, avec une appropriation limitée des cadres de gouvernance, des modèles d’innovation et des usages stratégiques de ces technologies.\n\n"
        "Consciente de ces enjeux, la Cité des Sciences et de l’Innovation de Guinée (CSIG), en partenariat avec l’Académie des Sciences de Guinée (ASG), a initié la Conférence DounIA – Données Numériques et Intelligence Artificielle comme un espace scientifique, indépendant et collaboratif de réflexion, d’échange et de cocréation autour des données numériques et de l’IA.\n\n"
        "La première édition, DounIA 1, s’est inscrite dans le cadre des orientations stratégiques nationales, notamment celles portées par le programme Simandou 2040, qui ambitionne une transformation structurelle du pays à travers la montée en compétences, la valorisation des talents locaux, la modernisation des secteurs productifs et le renforcement de la souveraineté technologique.\n\n"
        "Les travaux de DounIA 1 ont permis de mettre en évidence plusieurs défis structurants : déficit d’infrastructures numériques robustes, faible maturité en compétences digitales, absence de cadres clairs de gouvernance des données, et difficultés d’accès aux données publiques stratégiques. Ces contraintes limitent encore l’appropriation nationale de l’intelligence artificielle et son potentiel de contribution aux priorités de développement, notamment dans les domaines de l’éducation, de la santé, de l’agriculture, de la gestion publique et des zones à forte activité minière.\n\n"
        "À l’issue de cette première édition, un rapport de synthèse a été élaboré, consolidant les analyses, constats et premières pistes de réflexion issues des échanges entre chercheurs, experts, institutions publiques, acteurs du secteur privé et société civile.\n\n"
        "Dans une logique de redevabilité scientifique, de transparence et de continuité, la CSIG organise une cérémonie officielle de restitution de DounIA 1, couplée à une conférence de presse, afin de :"
    ))
    contexte_points = models.JSONField(default=list, blank=True)

    objectif_titre = models.CharField(max_length=200, default="Objectif de la cérémonie")
    objectif_general = models.TextField(default=(
        "Organiser une cérémonie officielle de restitution des résultats de DounIA 1, couplée à une conférence de presse, afin de partager les enseignements issus des travaux, d’annoncer la poursuite du processus avec DounIA 2, et de mobiliser les parties prenantes autour des prochaines étapes."
    ))
    objectifs_specifiques = models.JSONField(default=list, blank=True)

    resultats_titre = models.CharField(max_length=200, default="Résultats attendus")
    resultats_attendus = models.JSONField(default=list, blank=True)

    public_titre_ceremonie = models.CharField(max_length=200, default="Public cible")
    public_cible = models.JSONField(default=list, blank=True)
    
    # Section objectifs
    mission_titre = models.CharField(max_length=200, default="Mission Principale")
    mission_description = models.TextField(default="Présenter les synthèses des ateliers thématiques et les recommandations stratégiques pour une gouvernance inclusive des données et de l'IA en Guinée.")
    mission_points = models.JSONField(default=list, blank=True, help_text="Liste des points de la mission")
    
    public_titre = models.CharField(max_length=200, default="Public Ciblé")
    public_description = models.TextField(default="Cette restitution s'adresse à l'ensemble des acteurs impliqués dans la transformation numérique du pays.")
    public_points = models.JSONField(default=list, blank=True, help_text="Liste du public ciblé")
    
    # Section chiffres clés
    participants_nombre = models.CharField(max_length=50, default="150+")
    participants_label = models.CharField(max_length=100, default="Participants")
    
    ateliers_nombre = models.CharField(max_length=50, default="8")
    ateliers_label = models.CharField(max_length=100, default="Ateliers thématiques")
    
    recommandations_nombre = models.CharField(max_length=50, default="50+")
    recommandations_label = models.CharField(max_length=100, default="Recommandations")
    
    duree_nombre = models.CharField(max_length=50, default="3")
    duree_label = models.CharField(max_length=100, default="Mois de concertation")
    
    # Section rapports
    rapport_synthese_titre = models.CharField(max_length=200, default="Rapport Synthétique")
    rapport_synthese_description = models.TextField(default="Rapport complet présentant les conclusions et recommandations des ateliers DounIA.")
    rapport_synthese_fichier = models.FileField(upload_to='rapports/', blank=True, null=True)
    
    rapport_detail_titre = models.CharField(max_length=200, default="Recommandations Détaillées")
    rapport_detail_description = models.TextField(default="Document détaillé avec l'ensemble des recommandations par atelier thématique.")
    rapport_detail_fichier = models.FileField(upload_to='rapports/', blank=True, null=True)
    
    # Section chronologie
    chronologie = models.JSONField(default=list, blank=True, help_text="Liste des événements de la chronologie")
    
    # Section call-to-action
    cta_titre = models.CharField(max_length=200, default="Rejoignez la Démarche DounIA")
    cta_description = models.TextField(default="Participez à la construction de l'avenir numérique de la Guinée")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Restitution"
        verbose_name_plural = "Restitutions"
    
    def __str__(self):
        return self.titre_hero


class EvenementImage(models.Model):
    """Images pour les événements DounIA 1 et DounIA 2"""
    evenement = models.ForeignKey(DouniaEvent, on_delete=models.CASCADE, related_name='images', verbose_name='Événement')
    titre = models.CharField(max_length=200, verbose_name='Titre de l\'image')
    position = models.CharField(
        max_length=20,
        choices=[
            ('hero', 'Hero (arrière-plan)'),
            ('galerie', 'Galerie'),
        ],
        default='galerie',
        verbose_name='Position'
    )
    image = models.ImageField(upload_to='evenement_images/', blank=True, null=True, verbose_name='Image')
    image_url = models.URLField(max_length=500, blank=True, verbose_name='URL de l\'image (fallback)')
    description = models.TextField(blank=True, verbose_name='Description')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    active = models.BooleanField(default=True, verbose_name='Active')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')

    class Meta:
        verbose_name = 'Image d\'événement'
        verbose_name_plural = 'Images d\'événement'
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return f"{self.evenement} - {self.titre}"

    def get_image_url(self):
        """Retourne l'URL de l'image avec priorité à l'image uploadée"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80'


class RestitutionImage(models.Model):
    """Images pour la page de restitution"""
    restitution = models.ForeignKey(
        'Restitution',
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True,
        verbose_name='Restitution'
    )
    titre = models.CharField(max_length=200, verbose_name='Titre de l\'image')
    position = models.CharField(
        max_length=20,
        choices=[
            ('hero', 'Hero (arrière-plan)'),
            ('galerie', 'Galerie'),
        ],
        default='galerie',
        verbose_name='Position'
    )
    image = models.ImageField(upload_to='restitution_images/', blank=True, null=True, verbose_name='Image')
    image_url = models.URLField(max_length=500, blank=True, verbose_name='URL de l\'image (fallback)')
    description = models.TextField(blank=True, verbose_name='Description')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    active = models.BooleanField(default=True, verbose_name='Active')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')

    class Meta:
        verbose_name = 'Image de restitution'
        verbose_name_plural = 'Images de restitution'
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return self.titre

    def get_image_url(self):
        """Retourne l'URL de l'image avec priorité à l'image uploadée"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80'


class Atelier(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='Code')
    label = models.CharField(max_length=255, verbose_name='Libellé')
    description = models.TextField(blank=True, default='', verbose_name='Description')
    image = models.ImageField(upload_to='ateliers/', blank=True, null=True, verbose_name='Image')
    image_url = models.URLField(max_length=500, blank=True, default='', verbose_name='URL de l\'image')
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Atelier'
        verbose_name_plural = 'Ateliers'
        ordering = ['ordre', 'label']

    def __str__(self):
        return self.label

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        if self.image_url:
            return self.image_url
        return ''


class Inscription(models.Model):
    ATELIER_CHOICES = [
        ('education', 'Éducation, enseignement supérieur, recherche & innovation'),
        ('sante', 'Santé & inclusion sociale'),
        ('justice', 'Justice, sécurité & défense'),
        ('rh_entreprise', 'Ressources humaines, gestion d\'entreprise & secteur informel'),
        ('agriculture', 'Agriculture & développement rural'),
        ('mines_env', 'Mines, environnement, climat & biosphère'),
    ]

    PROFIL_CHOICES = [
        ('institution', 'Institution publique'),
        ('chercheur', 'Chercheur / Enseignant-chercheur'),
        ('etudiant', 'Étudiant'),
        ('entreprise', 'Entreprise / Startup tech'),
        ('ong', 'ONG / Société civile'),
        ('expert', 'Expert national ou international'),
        ('autre', 'Autre'),
    ]

    ENGAGEMENT_CHOICES = [
        ('participant', 'Participant'),
        ('contributeur', 'Contributeur actif'),
        ('observateur', 'Observateur'),
        ('intervenant', 'Intervenant / Expert'),
    ]

    FORMAT_CHOICES = [
        ('presentiel', 'Présentiel'),
        ('distanciel', 'Distanciel'),
        ('hybride', 'Hybride (présentiel + distanciel)'),
    ]

    DISPONIBILITE_CHOICES = [
        ('semaine', 'En semaine (journée)'),
        ('soir', 'En soirée'),
        ('weekend', 'Le week-end'),
        ('flexible', 'Flexible'),
    ]

    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    email = models.EmailField(verbose_name='Adresse email')
    whatsapp = models.CharField(max_length=20, verbose_name='Numéro WhatsApp')
    institution = models.CharField(max_length=200, verbose_name='Institution / Organisation')
    fonction = models.CharField(max_length=200, verbose_name='Fonction / Poste')
    profil = models.CharField(max_length=50, choices=PROFIL_CHOICES, verbose_name='Profil')
    profil_autre = models.CharField(max_length=200, blank=True, default='', verbose_name='Profil (autre, précisez)')
    atelier = models.CharField(max_length=50, choices=ATELIER_CHOICES, verbose_name='Atelier thématique choisi')
    engagement = models.CharField(max_length=50, choices=ENGAGEMENT_CHOICES, verbose_name='Engagement souhaité')
    format_preference = models.CharField(max_length=50, choices=FORMAT_CHOICES, verbose_name='Format préféré')
    disponibilite = models.CharField(max_length=50, choices=DISPONIBILITE_CHOICES, verbose_name='Disponibilité')
    motivation = models.TextField(max_length=500, blank=True, default='', verbose_name='Motivation (500 caractères max)')
    validation_engagement = models.BooleanField(default=False, verbose_name='Je m\'engage à participer activement aux travaux de l\'atelier choisi')
    date_inscription = models.DateTimeField(default=timezone.now, verbose_name='Date d\'inscription')
    valide = models.BooleanField(default=False, verbose_name='Inscription validée')
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name='Date de validation')

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.get_atelier_display()}"

    @property
    def atelier_label(self):
        try:
            atelier = Atelier.objects.filter(code=self.atelier).only('label').first()
            if atelier and atelier.label:
                return atelier.label
        except Exception:
            pass
        return dict(self.ATELIER_CHOICES).get(self.atelier, self.atelier)


class SiteConfiguration(models.Model):
    """Singleton — contenu éditable de toutes les sections de la landing page."""

    # HERO
    hero_badge = models.CharField(max_length=200, default='Guinée — Processus National', verbose_name='Hero badge')
    hero_titre = models.CharField(max_length=300, default='DounIA — Données Numériques & Intelligence Artificielle', verbose_name='Hero titre')
    hero_titre_span = models.CharField(max_length=200, blank=True, default='Guinée', verbose_name='Hero titre (partie en surbrillance)')
    hero_sous_titre = models.TextField(default="Un processus scientifique, collaboratif et indépendant visant à coconstruire une vision nationale autour de la gouvernance des données et de l'intelligence artificielle en Guinée.", verbose_name='Hero sous-titre')
    hero_description = models.TextField(default="Un processus scientifique, collaboratif et indépendant visant à coconstruire une vision nationale autour de la gouvernance des données et de l'intelligence artificielle en Guinée.", verbose_name='Hero description')
    hero_image = models.ImageField(upload_to='hero/', blank=True, null=True, verbose_name='Hero image (upload)')
    hero_image_url = models.URLField(blank=True, default='https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&q=80', verbose_name='Hero image URL (fallback)')
    hero_btn1_texte = models.CharField(max_length=100, default='Télécharger le rapport', verbose_name='Hero bouton 1 texte')
    hero_btn1_lien = models.CharField(max_length=300, default='#rapport', verbose_name='Hero bouton 1 lien')
    hero_btn2_texte = models.CharField(max_length=100, default="S'inscrire aux ateliers", verbose_name='Hero bouton 2 texte')
    hero_btn2_lien = models.CharField(max_length=300, default='#inscription', verbose_name='Hero bouton 2 lien')

    # ABOUT
    about_titre = models.CharField(max_length=200, default="C'est quoi DounIA ?", verbose_name='About titre')
    about_sous_titre = models.TextField(default="Comprendre les enjeux, structurer les réponses et bâtir une vision guinéenne autour de la donnée et de l'intelligence artificielle.", verbose_name='About sous-titre')
    about_card1_icone = models.CharField(max_length=50, default='bi-globe-africa', verbose_name='About card 1 icône')
    about_card1_titre = models.CharField(max_length=200, default='Un enjeu continental', verbose_name='About card 1 titre')
    about_card1_texte = models.TextField(default="L'Afrique fait face à des défis majeurs en matière de souveraineté numérique, de gouvernance des données et d'adoption de l'IA. DounIA s'inscrit dans cette dynamique continentale pour positionner la Guinée comme acteur de sa transformation digitale.", verbose_name='About card 1 texte')
    about_card2_icone = models.CharField(max_length=50, default='bi-diagram-3', verbose_name='About card 2 icône')
    about_card2_titre = models.CharField(max_length=200, default='Un processus structurant', verbose_name='About card 2 titre')
    about_card2_texte = models.TextField(default="DounIA est un cadre scientifique et indépendant qui réunit chercheurs, institutions, société civile et secteur privé pour coconstruire une approche nationale cohérente, inclusive et adaptée aux réalités guinéennes.", verbose_name='About card 2 texte')
    about_card3_icone = models.CharField(max_length=50, default='bi-lightbulb', verbose_name='About card 3 icône')
    about_card3_titre = models.CharField(max_length=200, default='Des ambitions concrètes', verbose_name='About card 3 titre')
    about_card3_texte = models.TextField(default="De la réflexion à l'action : DounIA vise à produire des recommandations opérationnelles, des feuilles de route sectorielles et des cadres de gouvernance adaptés au contexte guinéen et ouest-africain.", verbose_name='About card 3 texte')

    # DOUNIA 1
    dounia1_titre = models.CharField(max_length=200, default='DounIA 1 — Contexte & Enseignements', verbose_name='DounIA 1 titre')
    dounia1_sous_titre = models.TextField(default="La première édition a permis d'établir un diagnostic approfondi et de poser les bases d'un dialogue national structuré autour de l'IA et des données.", verbose_name='DounIA 1 sous-titre')
    dounia1_defis = models.TextField(default="Absence de cadre réglementaire spécifique à l'IA et à la protection des données personnelles\nFracture numérique persistante entre zones urbaines et rurales\nFaible capacité en recherche et innovation dans le domaine de l'IA\nManque de données structurées et ouvertes pour l'entraînement de modèles locaux", verbose_name='DounIA 1 défis (un par ligne)', help_text='Un défi par ligne')
    dounia1_opportunites = models.TextField(default="Potentiel élevé dans l'agriculture, la santé et l'éducation grâce à l'IA\nJeunesse dynamique et connectée, moteur d'innovation\nRessources naturelles dont la gestion peut être optimisée par les technologies numériques\nMobilisation croissante de la diaspora scientifique et technique", verbose_name='DounIA 1 opportunités (une par ligne)', help_text='Une opportunité par ligne')

    # RAPPORT
    rapport_titre = models.CharField(max_length=200, default='Rapport DounIA 1', verbose_name='Rapport titre')
    rapport_sous_titre = models.TextField(default="Consultez le rapport complet de la première édition de DounIA : diagnostic, recommandations et feuille de route pour la gouvernance de l'IA en Guinée.", verbose_name='Rapport sous-titre')
    rapport_description = models.TextField(default="Ce rapport présente les résultats de la première phase du processus DounIA, incluant l'état des lieux de l'écosystème numérique guinéen, les défis identifiés, les opportunités par secteur et les recommandations stratégiques pour une gouvernance responsable de l'IA.", verbose_name='Rapport description')
    rapport_points = models.TextField(default="Diagnostic de l'écosystème numérique\nAnalyse sectorielle approfondie\nRecommandations stratégiques\nFeuille de route opérationnelle", verbose_name='Rapport points clés (un par ligne)')
    rapport_lien = models.URLField(blank=True, default='', verbose_name='Lien de téléchargement du rapport')
    rapport_fichier = models.FileField(upload_to='rapports/', blank=True, null=True, verbose_name='Fichier PDF du rapport')
    rapport_image = models.ImageField(upload_to='rapports/', blank=True, null=True, verbose_name='Image de couverture du rapport')

    # PODCAST
    podcast_titre = models.CharField(max_length=200, default='Podcast DounIA', verbose_name='Podcast titre')
    podcast_description = models.TextField(default="Écoutez les échanges, interviews et analyses des experts ayant participé au processus DounIA. Des discussions autour de la gouvernance de l'IA, de la souveraineté numérique et des enjeux spécifiques à la Guinée et au continent africain.", verbose_name='Podcast description')
    podcast_lien = models.URLField(blank=True, default='', verbose_name='Lien du podcast')
    podcast_fichier = models.FileField(upload_to='podcasts/', blank=True, null=True, verbose_name='Fichier audio du podcast (MP3/WAV)')

    # DOUNIA 2
    dounia2_badge = models.CharField(max_length=200, default='Prochaine étape', verbose_name='DounIA 2 badge')
    dounia2_titre = models.CharField(max_length=200, default='DounIA 2 — La suite du processus', verbose_name='DounIA 2 titre')
    dounia2_description = models.TextField(default="Après la phase de diagnostic et de consultation, DounIA 2 marque le passage de la réflexion vers l'action. Des travaux sectoriels approfondis seront menés à travers des ateliers thématiques prévus pour octobre 2026, réunissant experts, praticiens et décideurs.", verbose_name='DounIA 2 description')
    dounia2_phase1 = models.TextField(default='Phase 1 — Diagnostic (terminée)|DounIA 1 : consultation nationale, 600+ participants, rapport publié.', verbose_name='Phase 1 (titre|description)')
    dounia2_phase2 = models.TextField(default='Phase 2 — Inscriptions & préparation|Ouverture des inscriptions aux ateliers thématiques, constitution des groupes de travail.', verbose_name='Phase 2 (titre|description)')
    dounia2_phase3 = models.TextField(default='Phase 3 — Ateliers sectoriels (Oct. 2026)|6 ateliers thématiques avec production de recommandations et feuilles de route.', verbose_name='Phase 3 (titre|description)')
    dounia2_phase4 = models.TextField(default='Phase 4 — Synthèse & publication|Rapport DounIA 2, plan d\'action national et présentation aux décideurs.', verbose_name='Phase 4 (titre|description)')

    # VIDEO
    video_titre = models.CharField(max_length=200, default='Vidéo de présentation', verbose_name='Titre de la section vidéo')
    video_sous_titre = models.TextField(default='Découvrez DounIA en images', verbose_name='Sous-titre de la section vidéo')
    video_lien = models.URLField(blank=True, default='', verbose_name='Lien vidéo (YouTube, Vimeo...)')
    video_fichier = models.FileField(upload_to='videos/', blank=True, null=True, verbose_name='Fichier vidéo (MP4)')

    # INSCRIPTION
    inscription_titre = models.CharField(max_length=200, default='Inscription aux Ateliers DounIA 2', verbose_name='Section inscription titre')
    inscription_sous_titre = models.TextField(default="Remplissez le formulaire ci-dessous pour vous inscrire à l'atelier thématique de votre choix. Tous les champs sont obligatoires.", verbose_name='Section inscription sous-titre')

    # SECTIONS LANDING — TITRES / SOUS-TITRES
    evenements_titre = models.CharField(max_length=200, default='Événements', verbose_name='Landing — Événements titre')
    evenements_sous_titre = models.TextField(default='DounIA 1 (objectifs, chiffres, images) et préparation de DounIA 2.', verbose_name='Landing — Événements sous-titre')
    experts_titre = models.CharField(max_length=200, default='Experts', verbose_name='Landing — Experts titre')
    experts_sous_titre = models.TextField(default='Experts intervenants dans le projet DounIA', verbose_name='Landing — Experts sous-titre')
    ateliers_titre = models.CharField(max_length=200, default='Ateliers Thématiques', verbose_name='Landing — Ateliers titre')
    ateliers_sous_titre = models.TextField(default="Six axes stratégiques pour construire une vision sectorielle de l'IA en Guinée.\nChoisissez votre atelier et inscrivez-vous.", verbose_name='Landing — Ateliers sous-titre')
    calendrier_titre = models.CharField(max_length=200, default='Calendrier des Ateliers', verbose_name='Landing — Calendrier titre')
    calendrier_sous_titre = models.TextField(default='Planification détaillée de chaque atelier thématique — Octobre 2026', verbose_name='Landing — Calendrier sous-titre')

    # LANDING — CALENDRIER (BACKGROUNDS)
    calendrier_bg_education = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background Éducation')
    calendrier_bg_sante = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background Santé')
    calendrier_bg_justice = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background Justice')
    calendrier_bg_rh = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background RH')
    calendrier_bg_finance = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background Finance')
    calendrier_bg_mines = models.ImageField(upload_to='calendrier/', blank=True, null=True, verbose_name='Calendrier — Background Mines')

    # PORTEURS
    porteur1_nom = models.CharField(max_length=200, default='CSIG', verbose_name='Porteur 1 — Nom')
    porteur1_description = models.CharField(max_length=300, default="Cité des Sciences et de l'Innovation de Guinée", verbose_name='Porteur 1 — Description')
    porteur1_logo = models.ImageField(upload_to='porteurs/', blank=True, null=True, verbose_name='Porteur 1 — Logo')
    porteur2_nom = models.CharField(max_length=200, default='ASG', verbose_name='Porteur 2 — Nom')
    porteur2_description = models.CharField(max_length=300, default='Académie des Sciences de Guinée', verbose_name='Porteur 2 — Description')
    porteur2_logo = models.ImageField(upload_to='porteurs/', blank=True, null=True, verbose_name='Porteur 2 — Logo')

    # FOOTER
    footer_description = models.TextField(default="DounIA est un processus scientifique national visant à coconstruire une vision guinéenne autour de l'IA et de la gouvernance des données.", verbose_name='Footer description')
    footer_email = models.EmailField(default='contact@dounia.gn', verbose_name='Email de contact')
    footer_lieu = models.CharField(max_length=200, default='Conakry, Guinée', verbose_name='Lieu')

    class Meta:
        verbose_name = 'Configuration du site'
        verbose_name_plural = 'Configuration du site'

    def __str__(self):
        return 'Configuration du site'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def video_embed_url(self):
        """Convertit un lien YouTube/Vimeo en URL d'embed avec autoplay"""
        import re
        url = self.video_lien or ''
        # YouTube: youtube.com/watch?v=ID ou youtu.be/ID
        yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', url)
        if yt:
            return f'https://www.youtube.com/embed/{yt.group(1)}'
        # Vimeo: vimeo.com/ID
        vm = re.search(r'vimeo\.com/(\d+)', url)
        if vm:
            return f'https://player.vimeo.com/video/{vm.group(1)}'
        return url

    @property
    def podcast_url(self):
        url = (self.podcast_lien or '').strip()
        if not url:
            return ''
        if url.startswith('http://') or url.startswith('https://'):
            return url
        return f'https://{url}'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ChiffreCle(models.Model):
    """Chiffres clés affichés dans la section statistiques."""
    EDITION_CHOICES = [
        ('dounia1', 'DounIA 1'),
        ('dounia2', 'DounIA 2'),
    ]

    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, default='dounia1', verbose_name='Édition')
    nombre = models.IntegerField(verbose_name='Nombre')
    suffixe = models.CharField(max_length=10, blank=True, default='+', verbose_name='Suffixe (ex: +)')
    label = models.CharField(max_length=100, verbose_name='Libellé')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')

    class Meta:
        verbose_name = 'Chiffre clé'
        verbose_name_plural = 'Chiffres clés'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nombre}{self.suffixe} {self.label}"


class Evenement(models.Model):
    EDITION_CHOICES = [
        ('dounia1', 'DounIA 1'),
        ('dounia2', 'DounIA 2'),
    ]

    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, unique=True, verbose_name='Édition')
    titre = models.CharField(max_length=200, default='', verbose_name='Titre')
    sous_titre = models.TextField(blank=True, default='', verbose_name='Sous-titre')
    objectifs = models.TextField(blank=True, default='', verbose_name='Objectifs (un par ligne)')

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['edition']

    def __str__(self):
        return self.get_edition_display()


class Expert(models.Model):
    """Experts et participants affichés sur la page."""
    nom = models.CharField(max_length=200, verbose_name='Nom')
    specialite = models.CharField(max_length=200, verbose_name='Spécialité')
    photo = models.ImageField(upload_to='experts/', blank=True, null=True, verbose_name='Photo')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')

    class Meta:
        verbose_name = 'Expert'
        verbose_name_plural = 'Experts'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} — {self.specialite}"


class Partenaire(models.Model):
    """Partenaires et institutions affichés sur la page."""
    CATEGORIE_CHOICES = [
        ('institutionnel', 'Partenaire institutionnel'),
        ('technique', 'Partenaire technique'),
    ]

    nom = models.CharField(max_length=200, verbose_name='Nom')
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='institutionnel', verbose_name='Catégorie')
    logo = models.ImageField(upload_to='partenaires/', blank=True, null=True, verbose_name='Logo')
    site_web = models.URLField(blank=True, default='', verbose_name='Site web')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')

    class Meta:
        verbose_name = 'Partenaire'
        verbose_name_plural = 'Partenaires'
        ordering = ['ordre']

    def __str__(self):
        return self.nom


class HeroCarouselImage(models.Model):
    """Images pour le carrousel de la section hero"""
    titre = models.CharField(max_length=200, verbose_name='Titre de l\'image')
    image = models.ImageField(upload_to='hero_carousel/', blank=True, null=True, verbose_name='Image (upload)')
    image_url = models.URLField(blank=True, verbose_name='URL de l\'image (alternative)')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    active = models.BooleanField(default=True, verbose_name='Active')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')
    
    class Meta:
        verbose_name = 'Image du carrousel Hero'
        verbose_name_plural = 'Images du carrousel Hero'
        ordering = ['ordre', 'date_ajout']
    
    def __str__(self):
        return f"{self.titre} (#{self.ordre})"
    
    def get_image_url(self):
        """Retourne l'URL de l'image locale ou de l'URL externe"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            # Image par défaut
            return "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&q=80"
