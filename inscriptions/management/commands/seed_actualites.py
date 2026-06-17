from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from inscriptions.models import Rubrique, Article


RUBRIQUES = [
    {"nom": "Événements", "couleur": "#003366", "ordre": 1,
     "description": "Couverture des temps forts et rencontres du projet DounIA."},
    {"nom": "Ateliers", "couleur": "#0d6efd", "ordre": 2,
     "description": "Formations, ateliers thématiques et renforcement de capacités."},
    {"nom": "Partenariats", "couleur": "#198754", "ordre": 3,
     "description": "Accords, coopérations et signatures avec nos partenaires."},
    {"nom": "Communiqués", "couleur": "#6c757d", "ordre": 4,
     "description": "Annonces et communications officielles du projet."},
]


ARTICLES = [
    {
        "titre": "Lancement officiel du projet DounIA à Conakry",
        "rubrique": "Événements",
        "epingle": True,
        "tags": "DounIA, Lancement, Conakry, Intelligence Artificielle",
        "chapo": "Le projet DounIA a été officiellement lancé à Conakry en présence des autorités nationales et des partenaires techniques et financiers.",
        "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Cérémonie de lancement du projet DounIA à Conakry.",
        "corps": """
<p>Le projet <strong>DounIA</strong> a été officiellement lancé ce vendredi à Conakry, marquant une étape déterminante
dans la stratégie nationale de développement de l'intelligence artificielle en République de Guinée. La cérémonie
s'est tenue en présence de plusieurs membres du Gouvernement, de représentants du secteur privé et de la communauté
scientifique.</p>

<p>Porté par la Cité des Sciences et de l'Innovation de Guinée (CSIG), le projet vise à faire émerger un écosystème
local de la donnée et de l'intelligence artificielle, au service du développement économique et social du pays.</p>

<h2>Une ambition nationale</h2>
<p>Dans son intervention, le Secrétaire Général a rappelé que DounIA s'inscrit dans la vision des plus hautes autorités
nationales, en faveur d'une Guinée numérique, souveraine et inclusive. Il a souligné l'importance de former une nouvelle
génération de talents capables de relever les défis technologiques de demain.</p>

<blockquote>« L'intelligence artificielle n'est pas un luxe, mais un levier stratégique pour notre développement »,
a-t-il déclaré devant l'assistance.</blockquote>

<h2>Les prochaines étapes</h2>
<ul>
<li>Mise en place des premiers ateliers thématiques dès le mois prochain ;</li>
<li>Constitution d'un réseau d'experts nationaux et internationaux ;</li>
<li>Ouverture d'un programme de formation à destination des jeunes diplômés.</li>
</ul>

<p>Le projet entend ainsi poser les bases d'une transformation durable, en plaçant la donnée et l'IA au cœur des
politiques publiques.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
    {
        "titre": "Atelier de formation sur la science des données pour les jeunes diplômés",
        "rubrique": "Ateliers",
        "epingle": True,
        "tags": "Formation, Data Science, Jeunesse, Compétences",
        "chapo": "Un atelier intensif de science des données a réuni des dizaines de jeunes diplômés autour des fondamentaux de l'analyse et de la modélisation.",
        "image_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Les participants à l'atelier de science des données.",
        "corps": """
<p>Dans le cadre de ses activités de renforcement de capacités, le projet <strong>DounIA</strong> a organisé un atelier
intensif de <strong>science des données</strong> destiné aux jeunes diplômés en informatique, mathématiques et statistiques.</p>

<p>Pendant plusieurs jours, les participants ont été initiés aux fondamentaux de la collecte, du nettoyage et de
l'analyse des données, ainsi qu'aux premières techniques de modélisation prédictive.</p>

<h2>Un apprentissage par la pratique</h2>
<p>L'atelier a privilégié une approche concrète, avec des études de cas inspirées de problématiques locales :
agriculture, santé publique, mobilité urbaine et services administratifs.</p>

<ul>
<li>Manipulation de jeux de données réels ;</li>
<li>Initiation aux outils open source ;</li>
<li>Travaux de groupe et restitutions collectives.</li>
</ul>

<p>À l'issue de la formation, les participants ont reçu une attestation et ont été invités à intégrer la communauté
des praticiens DounIA, afin de poursuivre leur montée en compétences.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
    {
        "titre": "Signature d'un partenariat stratégique pour l'innovation",
        "rubrique": "Partenariats",
        "epingle": True,
        "tags": "Partenariat, Coopération, Innovation",
        "chapo": "Un accord de coopération a été signé afin de renforcer les capacités locales en matière de recherche et d'innovation.",
        "image_url": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Signature de l'accord de partenariat.",
        "corps": """
<p>Le projet <strong>DounIA</strong> a procédé à la signature d'un <strong>partenariat stratégique</strong> visant à
renforcer les capacités nationales en matière de recherche, d'innovation et de formation dans le domaine de
l'intelligence artificielle.</p>

<p>Cet accord prévoit notamment des échanges d'expertise, l'accès à des ressources techniques et la mise en place de
programmes conjoints au bénéfice des étudiants et chercheurs guinéens.</p>

<h2>Des engagements concrets</h2>
<ul>
<li>Mobilité académique et scientifique ;</li>
<li>Accompagnement de projets innovants portés par des jeunes ;</li>
<li>Appui à la création d'infrastructures de calcul.</li>
</ul>

<p>Les deux parties ont salué la qualité du dialogue et réaffirmé leur volonté de bâtir une coopération durable, au
service du développement technologique du pays.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
    {
        "titre": "DounIA présente ses premiers résultats lors d'une restitution publique",
        "rubrique": "Événements",
        "epingle": False,
        "tags": "Restitution, Résultats, Recherche",
        "chapo": "Une session de restitution publique a permis de partager les premiers résultats et perspectives du projet avec le grand public.",
        "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Séance de restitution publique des travaux DounIA.",
        "corps": """
<p>Le projet <strong>DounIA</strong> a tenu une session de <strong>restitution publique</strong> au cours de laquelle
ses équipes ont partagé les premiers résultats de leurs travaux, ainsi que les perspectives à venir.</p>

<p>Cette rencontre, ouverte à un large public, a permis d'échanger autour des usages concrets de l'intelligence
artificielle et de la donnée dans le contexte guinéen.</p>

<h2>Des échanges nourris</h2>
<p>Étudiants, chercheurs, entrepreneurs et représentants institutionnels ont pris part aux discussions, posant de
nombreuses questions sur l'éthique, la souveraineté des données et l'impact économique attendu.</p>

<p>Les organisateurs ont annoncé la tenue de prochaines sessions thématiques, afin de poursuivre la dynamique de
dialogue entre la science et la société.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
    {
        "titre": "Communiqué : ouverture des candidatures au programme de formation",
        "rubrique": "Communiqués",
        "epingle": False,
        "tags": "Candidatures, Formation, Programme",
        "chapo": "Les candidatures au programme de formation DounIA sont officiellement ouvertes aux jeunes talents intéressés par l'IA et la donnée.",
        "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Ouverture des candidatures au programme de formation.",
        "corps": """
<p>Le projet <strong>DounIA</strong> annonce l'ouverture officielle des <strong>candidatures</strong> à son programme de
formation dédié à l'intelligence artificielle et à la science des données.</p>

<p>Ce programme s'adresse aux jeunes diplômés et professionnels souhaitant développer des compétences avancées et
contribuer à l'essor de l'écosystème numérique national.</p>

<h2>Conditions de participation</h2>
<ul>
<li>Être titulaire d'un diplôme en sciences, technologies ou disciplines connexes ;</li>
<li>Démontrer une forte motivation pour les métiers de la donnée ;</li>
<li>Être disponible pour l'ensemble du cycle de formation.</li>
</ul>

<p>Les dossiers de candidature peuvent être déposés selon les modalités précisées prochainement sur les canaux
officiels du projet. Les places étant limitées, les candidats sont invités à postuler dans les meilleurs délais.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
    {
        "titre": "Rencontre avec les acteurs du numérique pour structurer l'écosystème local",
        "rubrique": "Partenariats",
        "epingle": False,
        "tags": "Écosystème, Numérique, Startups",
        "chapo": "Une rencontre de concertation a réuni startups, universités et institutions autour de la structuration de l'écosystème numérique.",
        "image_url": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1200&q=80",
        "image_legende": "Concertation avec les acteurs du numérique.",
        "corps": """
<p>Le projet <strong>DounIA</strong> a réuni les principaux <strong>acteurs du numérique</strong> lors d'une rencontre de
concertation consacrée à la structuration de l'écosystème local de l'innovation.</p>

<p>Startups, universités, incubateurs et institutions publiques ont échangé sur les défis communs et les leviers
permettant d'accélérer l'adoption des technologies de la donnée et de l'IA.</p>

<h2>Vers une feuille de route partagée</h2>
<p>Les participants ont convenu de la nécessité d'élaborer une feuille de route commune, articulée autour de la
formation, de l'accès aux infrastructures et du soutien aux projets innovants.</p>

<p>Cette dynamique de collaboration vise à créer un environnement favorable à l'émergence de solutions locales,
adaptées aux réalités et aux priorités du pays.</p>
<p><em>Service Communication et Relations Publiques</em></p>
""",
    },
]


class Command(BaseCommand):
    help = "Génère des rubriques et des articles de démonstration pour la section Actualités."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help="Supprime les articles et rubriques de démo avant de recréer."
        )

    def handle(self, *args, **options):
        if options.get('reset'):
            deleted_articles = Article.objects.filter(
                titre__in=[a['titre'] for a in ARTICLES]
            ).delete()
            self.stdout.write(self.style.WARNING(
                f"Articles de démo supprimés: {deleted_articles}"
            ))

        # Rubriques
        rubriques_map = {}
        for r in RUBRIQUES:
            obj, created = Rubrique.objects.get_or_create(
                nom=r['nom'],
                defaults={
                    'couleur': r['couleur'],
                    'ordre': r['ordre'],
                    'description': r['description'],
                    'active': True,
                },
            )
            if not created:
                obj.couleur = r['couleur']
                obj.ordre = r['ordre']
                obj.description = r['description']
                obj.active = True
                obj.save()
            rubriques_map[r['nom']] = obj
            self.stdout.write(self.style.SUCCESS(
                f"Rubrique {'créée' if created else 'mise à jour'} : {obj.nom}"
            ))

        # Articles
        now = timezone.now()
        for i, a in enumerate(ARTICLES):
            date_pub = now - timedelta(days=i * 3, hours=i)
            defaults = {
                'chapo': a['chapo'].strip(),
                'corps': a['corps'].strip(),
                'image_url': a.get('image_url', ''),
                'image_legende': a.get('image_legende', ''),
                'rubrique': rubriques_map.get(a['rubrique']),
                'tags': a.get('tags', ''),
                'auteur_nom': 'Rédaction DounIA',
                'statut': 'publie',
                'visibilite': 'public',
                'date_publication': date_pub,
                'epingle': a.get('epingle', False),
                'meta_description': a['chapo'].strip()[:160],
            }
            obj, created = Article.objects.get_or_create(
                titre=a['titre'], defaults=defaults
            )
            if not created:
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
            self.stdout.write(self.style.SUCCESS(
                f"Article {'créé' if created else 'mis à jour'} : {obj.titre}"
            ))

        self.stdout.write(self.style.SUCCESS(
            "\nContenu de démonstration généré avec succès. Visitez /actualites/"
        ))
