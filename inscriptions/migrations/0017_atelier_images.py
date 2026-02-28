from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0016_atelier'),
    ]

    operations = [
        migrations.AddField(
            model_name='atelier',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='ateliers/', verbose_name='Image'),
        ),
        migrations.AddField(
            model_name='atelier',
            name='image_url',
            field=models.URLField(blank=True, default='', max_length=500, verbose_name="URL de l'image"),
        ),
    ]
