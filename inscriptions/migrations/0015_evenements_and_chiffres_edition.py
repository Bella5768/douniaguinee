from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0014_siteconfiguration_podcast_fichier'),
    ]

    operations = [
        migrations.AddField(
            model_name='chiffrecle',
            name='edition',
            field=models.CharField(choices=[('dounia1', 'DounIA 1'), ('dounia2', 'DounIA 2')], default='dounia1', max_length=20, verbose_name='Édition'),
        ),
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edition', models.CharField(choices=[('dounia1', 'DounIA 1'), ('dounia2', 'DounIA 2')], max_length=20, unique=True, verbose_name='Édition')),
                ('titre', models.CharField(default='', max_length=200, verbose_name='Titre')),
                ('sous_titre', models.TextField(blank=True, default='', verbose_name='Sous-titre')),
                ('objectifs', models.TextField(blank=True, default='', verbose_name='Objectifs (un par ligne)')),
            ],
            options={
                'verbose_name': 'Événement',
                'verbose_name_plural': 'Événements',
                'ordering': ['edition'],
            },
        ),
        migrations.CreateModel(
            name='EvenementImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(blank=True, default='', max_length=200, verbose_name='Titre')),
                ('image', models.ImageField(blank=True, null=True, upload_to='evenements/', verbose_name='Image (upload)')),
                ('image_url', models.URLField(blank=True, default='', verbose_name="URL de l'image (alternative)")),
                ('ordre', models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('date_ajout', models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")),
                ('evenement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='inscriptions.evenement', verbose_name='Événement')),
            ],
            options={
                'verbose_name': "Image d'événement",
                'verbose_name_plural': "Images d'événement",
                'ordering': ['evenement', 'ordre', 'date_ajout'],
            },
        ),
    ]
