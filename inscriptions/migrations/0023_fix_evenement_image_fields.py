# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0022_fix_evenement_image_conflict'),
    ]

    operations = [
        # Ajouter le champ description s'il n'existe pas
        migrations.AddField(
            model_name='evenementimage',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        # S'assurer que le champ image peut être null
        migrations.AlterField(
            model_name='evenementimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='evenement_images/', verbose_name='Image'),
        ),
        # S'assurer que le champ image_url existe
        migrations.AddField(
            model_name='evenementimage',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, verbose_name='URL de l\'image (fallback)'),
        ),
    ]
