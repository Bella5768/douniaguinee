from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from inscriptions.models import Inscription, Atelier, SiteConfiguration, Expert, Partenaire, ChiffreCle, HeroCarouselImage, HeroImage, StatsImage, EvenementImage, RestitutionImage, DouniaEvent, Restitution, Avis


class Command(BaseCommand):
    help = 'Crée les groupes et utilisateurs par défaut avec des privilèges prédéfinis'

    def handle(self, *args, **options):
        self.stdout.write('Configuration des utilisateurs et groupes avec privilèges...')
        
        # Créer les groupes avec leurs privilèges
        self.create_groups()
        
        # Créer les utilisateurs par défaut
        self.create_default_users()
        
        self.stdout.write(self.style.SUCCESS('Configuration terminée avec succès!'))

    def create_groups(self):
        """Crée les groupes avec des permissions spécifiques"""
        
        # Groupe: Administrateurs (accès complet)
        admin_group, created = Group.objects.get_or_create(name='Administrateurs')
        if created:
            self.stdout.write('Groupe "Administrateurs" créé')
        
        # Groupe: Éditeurs (peut modifier le contenu mais pas les utilisateurs)
        editors_group, created = Group.objects.get_or_create(name='Éditeurs')
        if created:
            self.stdout.write('Groupe "Éditeurs" créé')
            # Permissions pour les éditeurs
            models_to_edit = [
                Inscription, Atelier, SiteConfiguration, Expert, Partenaire, 
                ChiffreCle, HeroCarouselImage, HeroImage, StatsImage, 
                EvenementImage, RestitutionImage, DouniaEvent, Restitution, Avis
            ]
            for model in models_to_edit:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(content_type=content_type)
                editors_group.permissions.set(permissions)
        
        # Groupe: Lecteurs (lecture seule)
        readers_group, created = Group.objects.get_or_create(name='Lecteurs')
        if created:
            self.stdout.write('Groupe "Lecteurs" créé')
            # Permissions de lecture seule (view)
            models_to_view = [
                Inscription, Atelier, SiteConfiguration, Expert, Partenaire, 
                ChiffreCle, HeroCarouselImage, HeroImage, StatsImage, 
                EvenementImage, RestitutionImage, DouniaEvent, Restitution, Avis
            ]
            for model in models_to_view:
                content_type = ContentType.objects.get_for_model(model)
                view_permissions = Permission.objects.filter(
                    content_type=content_type, 
                    codename__startswith='view_'
                )
                readers_group.permissions.set(view_permissions)

    def create_default_users(self):
        """Crée les utilisateurs par défaut avec des rôles prédéfinis"""
        
        # Administrateur principal (superuser)
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@dounia.gn',
                password='admin123',  # À changer en production!
                first_name='Administrateur',
                last_name='Principal'
            )
            admin_user.groups.add(Group.objects.get(name='Administrateurs'))
            self.stdout.write('Utilisateur "admin" créé (mot de passe: admin123)')
        else:
            self.stdout.write('Utilisateur "admin" existe déjà')
        
        # Éditeur exemple
        if not User.objects.filter(username='editeur').exists():
            editor_user = User.objects.create_user(
                username='editeur',
                email='editeur@dounia.gn',
                password='editeur123',
                first_name='Éditeur',
                last_name='Site',
                is_staff=True
            )
            editor_user.groups.add(Group.objects.get(name='Éditeurs'))
            self.stdout.write('Utilisateur "editeur" créé (mot de passe: editeur123)')
        else:
            self.stdout.write('Utilisateur "editeur" existe déjà')
        
        # Lecteur exemple
        if not User.objects.filter(username='lecteur').exists():
            reader_user = User.objects.create_user(
                username='lecteur',
                email='lecteur@dounia.gn',
                password='lecteur123',
                first_name='Lecteur',
                last_name='Site',
                is_staff=True
            )
            reader_user.groups.add(Group.objects.get(name='Lecteurs'))
            self.stdout.write('Utilisateur "lecteur" créé (mot de passe: lecteur123)')
        else:
            self.stdout.write('Utilisateur "lecteur" existe déjà')
