# Gestion des Utilisateurs - Documentation

## Accès à l'Admin Django

L'interface d'administration Django est accessible via: `/admin/`

## Groupes et Privilèges

### 1. Administrateurs
- **Accès complet** à toute l'interface d'administration
- Peut créer, modifier, supprimer tous les utilisateurs
- Peut gérer tous les modèles du site
- Accès aux paramètres système

### 2. Éditeurs
- Peut **modifier le contenu** du site mais pas les utilisateurs
- Modèles accessibles:
  - Inscriptions
  - Ateliers
  - Configuration du site
  - Experts
  - Partenaires
  - Chiffres clés
  - Images (Hero, Stats, Carousel, etc.)
  - Événements DounIA
  - Restitution
  - Avis
- **Pas d'accès** à la gestion des utilisateurs

### 3. Lecteurs
- **Lecture seule** sur tous les modèles de contenu
- Peut visualiser mais pas modifier
- Utile pour les utilisateurs qui doivent seulement consulter les données

## Utilisateurs par Défaut

### Administrateur Principal
- **Username**: `admin`
- **Mot de passe**: `admin123` (⚠️ À changer en production!)
- **Rôle**: Superutilisateur avec tous les privilèges
- **Email**: admin@dounia.gn

### Éditeur
- **Username**: `editeur`
- **Mot de passe**: `editeur123`
- **Rôle**: Membre du groupe "Éditeurs"
- **Email**: editeur@dounia.gn
- **Permissions**: Modification du contenu uniquement

### Lecteur
- **Username**: `lecteur`
- **Mot de passe**: `lecteur123`
- **Rôle**: Membre du groupe "Lecteurs"
- **Email**: lecteur@dounia.gn
- **Permissions**: Lecture seule

## Configuration Initiale

Pour recréer les groupes et utilisateurs par défaut:

```bash
python manage.py setup_admin_users
```

Cette commande:
1. Crée les trois groupes (Administrateurs, Éditeurs, Lecteurs)
2. Attribue les permissions appropriées à chaque groupe
3. Crée les utilisateurs par défaut s'ils n'existent pas

## Création de Nouveaux Utilisateurs

### Via l'Admin Django
1. Connectez-vous à `/admin/`
2. Allez dans "Authentication and Authorization" → "Users"
3. Cliquez sur "ADD USER"
4. Remplissez les informations personnelles
5. Dans la section "Privilèges et permissions":
   - Cochez `is_staff` pour permettre l'accès à l'admin
   - Cochez `is_superuser` pour un accès complet
   - Assignez un groupe (Administrateurs, Éditeurs, ou Lecteurs)

### Via Commande Django
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Créer un utilisateur avec script personnalisé
python manage.py shell
```

Puis dans le shell:
```python
from django.contrib.auth.models import User, Group

# Créer un utilisateur
user = User.objects.create_user(
    username='nouveau_user',
    email='user@example.com',
    password='mot_de_passe',
    first_name='Prénom',
    last_name='Nom',
    is_staff=True
)

# Assigner à un groupe
editor_group = Group.objects.get(name='Éditeurs')
user.groups.add(editor_group)
```

## Personnalisation des Permissions

### Modifier les permissions d'un groupe
1. Allez dans `/admin/auth/group/`
2. Sélectionnez le groupe à modifier
3. Cochez/décochez les permissions souhaitées
4. Sauvegardez

### Créer un nouveau groupe
1. Allez dans `/admin/auth/group/`
2. Cliquez sur "ADD GROUP"
3. Donnez un nom au groupe
4. Sélectionnez les permissions
5. Sauvegardez

## Sécurité

⚠️ **IMPORTANT**: En production:
1. Changez tous les mots de passe par défaut
2. Utilisez des mots de passe forts
3. Limitez le nombre de superutilisateurs
4. Révisez régulièrement les permissions des utilisateurs
5. Activez HTTPS
6. Configurez `ALLOWED_HOSTS` correctement

## Interface Admin Personnalisée

L'admin des utilisateurs a été personnalisé avec:
- Affichage des informations clés (username, email, nom, statut)
- Filtres par rôle et statut
- Recherche par nom, email, username
- Organisation des champs en sections logiques
- Privilèges regroupés dans une section dédiée

## Accès à l'Admin Custom (Gestion)

Le site dispose également d'une interface de gestion personnalisée accessible via:
- `/gestion/` - Dashboard
- `/gestion/utilisateurs/` - Gestion des utilisateurs (interface custom)

Cette interface custom coexiste avec l'admin Django standard.
