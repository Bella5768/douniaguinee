from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0024_restitutionimage_restitution'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenementimage',
            name='position',
            field=models.CharField(choices=[('hero', 'Hero (arrière-plan)'), ('galerie', 'Galerie')], default='galerie', max_length=20, verbose_name='Position'),
        ),
        migrations.AddField(
            model_name='restitutionimage',
            name='position',
            field=models.CharField(choices=[('hero', 'Hero (arrière-plan)'), ('galerie', 'Galerie')], default='galerie', max_length=20, verbose_name='Position'),
        ),
    ]
