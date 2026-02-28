from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0023_fix_evenement_image_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='restitutionimage',
            name='restitution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='inscriptions.restitution', verbose_name='Restitution'),
        ),
    ]
