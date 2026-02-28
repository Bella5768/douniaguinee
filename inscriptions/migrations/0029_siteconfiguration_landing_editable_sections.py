from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0028_restitution_hero_image_restitution_hero_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='hero_sous_titre',
            field=models.TextField(default="Un processus scientifique, collaboratif et indépendant visant à coconstruire une vision nationale autour de la gouvernance des données et de l'intelligence artificielle en Guinée.", verbose_name='Hero sous-titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='hero_titre_span',
            field=models.CharField(blank=True, default='Guinée', max_length=200, verbose_name='Hero titre (partie en surbrillance)'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='evenements_titre',
            field=models.CharField(default='Événements', max_length=200, verbose_name='Landing — Événements titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='evenements_sous_titre',
            field=models.TextField(default='DounIA 1 (objectifs, chiffres, images) et préparation de DounIA 2.', verbose_name='Landing — Événements sous-titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='experts_titre',
            field=models.CharField(default='Experts', max_length=200, verbose_name='Landing — Experts titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='experts_sous_titre',
            field=models.TextField(default='Experts intervenants dans le projet DounIA', verbose_name='Landing — Experts sous-titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='ateliers_titre',
            field=models.CharField(default='Ateliers Thématiques', max_length=200, verbose_name='Landing — Ateliers titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='ateliers_sous_titre',
            field=models.TextField(default="Six axes stratégiques pour construire une vision sectorielle de l'IA en Guinée.\nChoisissez votre atelier et inscrivez-vous.", verbose_name='Landing — Ateliers sous-titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_titre',
            field=models.CharField(default='Calendrier des Ateliers', max_length=200, verbose_name='Landing — Calendrier titre'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_sous_titre',
            field=models.TextField(default='Planification détaillée de chaque atelier thématique — Octobre 2026', verbose_name='Landing — Calendrier sous-titre'),
        ),
    ]
