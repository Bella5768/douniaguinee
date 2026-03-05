from django.db import migrations


def seed_restitution_agenda(apps, schema_editor):
    Restitution = apps.get_model('inscriptions', 'Restitution')

    try:
        obj = Restitution.objects.get(pk=1)
    except Restitution.DoesNotExist:
        return

    changed = False

    if not obj.agenda_date:
        obj.agenda_date = "Mercredi le 01 Avril 2026"
        changed = True

    if not obj.agenda_duree:
        obj.agenda_duree = "3 heures (09h00 – 12h00)"
        changed = True

    if not obj.agenda_invites:
        obj.agenda_invites = "~100"
        changed = True

    if not obj.agenda_sessions:
        obj.agenda_sessions = [
            {
                'heure': '09h00 – 09h30',
                'titre': "Arrivée, accueil et installation des invités",
                'details': (
                    "Fond sonore discret (instrumental, moderne, africain contemporain)\n"
                    "Diffusion en boucle sur écran : chiffres clés DounIA, citations fortes issues du rapport, "
                    "messages clés sur données & IA en Afrique."
                ),
            },
            {
                'heure': '09h30 – 10h00',
                'titre': "Cérémonie officielle d’ouverture",
                'details': (
                    "Mot de bienvenue de Pr. Abdoulaye Baniré Diallo, Coordinateur Général de la Cité des Sciences et de l’Innovation de Guinée (CSIG)\n"
                    "Allocution de Pr Baldé, Directeur de l’Académie des Sciences de Guinee (ASG)\n"
                    "Allocution de Dre Diaka Sidibé, Ministre de l’Enseignement Supérieur et de la Recherche Scientifique"
                ),
            },
            {
                'heure': '10h00 – 10h10',
                'titre': "Présentation Vidéo « ce que DounIA 1 nous a appris »",
                'details': "",
            },
            {
                'heure': '10h10 – 10h30',
                'titre': "Restitution Scientifique de DounIA 1 / Lancement de DounIA.org",
                'details': (
                    "Présentation du rapport DounIA 1\n"
                    "Présentation des ateliers thématiques : Points clés, Pourquoi ils sont stratégiques, "
                    "À qui ils s’adressent et Comment participer\n\n"
                    "Présentateurs :\n"
                    "Bany Bah, Coordinatrice Générale de DounIA\n"
                    "Pr Gayo Diallo, Président du Comité Scientifique DounIA 1"
                ),
            },
            {
                'heure': '10h30 – 10h50',
                'titre': "Remise officielle des attestations – DounIA 1",
                'details': (
                    "Comité scientifique\n"
                    "Experts scientifiques\n"
                    "Lead des tables rondes thématiques\n\n"
                    "Présentateur : Pr Gayo Diallo, Président du Comité Scientifique DounIA 1"
                ),
            },
            {
                'heure': '11h00 – 11h30',
                'titre': "CONFÉRENCE DE PRESSE (30 min)",
                'details': "",
            },
            {
                'heure': '11h30 – 12h00',
                'titre': "Clôture et Engagements",
                'details': (
                    "Remerciements ciblés\n"
                    "Appel à engagement\n"
                    "Signature solennelle du Manifeste de Conakry\n"
                    "Cocktail"
                ),
            },
        ]
        changed = True

    if changed:
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0035_restitution_agenda_date_restitution_agenda_duree_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_restitution_agenda, migrations.RunPython.noop),
    ]
