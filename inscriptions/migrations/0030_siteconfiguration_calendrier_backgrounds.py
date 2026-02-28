from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0029_siteconfiguration_landing_editable_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_education',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background Éducation'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_sante',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background Santé'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_justice',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background Justice'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_rh',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background RH'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_finance',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background Finance'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='calendrier_bg_mines',
            field=models.ImageField(blank=True, null=True, upload_to='calendrier/', verbose_name='Calendrier — Background Mines'),
        ),
    ]
