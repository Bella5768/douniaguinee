from django.db import migrations, models


def seed_ateliers(apps, schema_editor):
    Atelier = apps.get_model('inscriptions', 'Atelier')
    Inscription = apps.get_model('inscriptions', 'Inscription')

    if Atelier.objects.exists():
        return

    try:
        choices = getattr(Inscription, 'ATELIER_CHOICES', [])
    except Exception:
        choices = []

    for i, item in enumerate(choices):
        if not item or len(item) < 2:
            continue
        code, label = item[0], item[1]
        Atelier.objects.create(code=code, label=label, ordre=i, active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0015_evenements_and_chiffres_edition'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atelier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Code')),
                ('label', models.CharField(max_length=255, verbose_name='Libellé')),
                ('ordre', models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('active', models.BooleanField(default=True, verbose_name='Actif')),
            ],
            options={
                'verbose_name': 'Atelier',
                'verbose_name_plural': 'Ateliers',
                'ordering': ['ordre', 'label'],
            },
        ),
        migrations.RunPython(seed_ateliers, migrations.RunPython.noop),
    ]
