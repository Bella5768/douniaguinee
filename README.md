# DounIA — Plateforme Données Numériques & Intelligence Artificielle

Landing page et système d'inscription pour le processus DounIA en Guinée.

## Stack technique

- **Backend** : Django 4.2
- **Frontend** : HTML, CSS, JavaScript, Bootstrap 5
- **Base de données** : SQLite (MVP) / PostgreSQL (production)
- **Formulaires** : django-crispy-forms + Bootstrap 5

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur (accès admin)
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

## Accès

- **Landing page** : http://localhost:8000/
- **Admin** : http://localhost:8000/admin/
- **Export CSV** : http://localhost:8000/export-csv/ (staff uniquement)

## Configuration email (production)

Dans le fichier `.env`, configurez :

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votreserveur.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.com
EMAIL_HOST_PASSWORD=motdepasse
DEFAULT_FROM_EMAIL=noreply@dounia.gn
```

## Structure du projet

```
Landing_page_DOUNIA/
├── dounia_project/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inscriptions/            # Application principale
│   ├── models.py            # Modèle Inscription (12 champs)
│   ├── forms.py             # Formulaire avec validation
│   ├── views.py             # Vues (landing, inscription, export CSV)
│   ├── admin.py             # Admin avec filtrage et export
│   └── urls.py
├── templates/               # Templates HTML
│   ├── base.html
│   └── inscriptions/
│       ├── landing.html     # Landing page complète (12 sections)
│       └── confirmation.html
├── static/
│   ├── css/style.css        # Styles personnalisés
│   └── js/main.js           # JavaScript (animations, formulaire)
├── manage.py
├── requirements.txt
└── .env
```
