from django.db import migrations


def seed_atelier_details(apps, schema_editor):
    Atelier = apps.get_model('inscriptions', 'Atelier')

    ateliers = [
        {
            'code': 'EESR',
            'label': "Éducation, enseignement supérieur, recherche & innovation",
            'description': "Exploration de l'IA dans l'éducation : personnalisation des apprentissages, outils pédagogiques, et préparation aux métiers de demain.",
            'ordre': 1,
            'objectif': (
                "Cette table ronde explorera comment l'IA peut transformer l'éducation en\n"
                "Guinée, en se concentrant sur la personnalisation des parcours d'apprentissage,\n"
                "l'intégration de l'IA comme outil pédagogique, et la préparation de la jeunesse aux\n"
                "métiers de demain. Elle examinera également les stratégies pour former les\n"
                "enseignants à utiliser efficacement l'IA et les compétences numériques, tout en\n"
                "veillant à ce que l'intégration de l'IA ne creuse pas les inégalités."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Comment l'IA peut-elle aider à créer des outils pédagogiques adaptatifs pour "
                "améliorer les résultats scolaires et lutter contre le décrochage en Guinée ?</li>"
                "<li>Quelles stratégies mettre en place pour former efficacement les enseignants "
                "à l'utilisation pédagogique des outils d'IA et à l'enseignement des "
                "compétences numériques fondamentales ?</li>"
                "<li>Comment s'assurer que l'intégration de l'IA dans l'éducation ne creuse pas "
                "les inégalités (accès aux technologies, fracture numérique) et respecte "
                "l'éthique ?</li>"
                "<li>Quels contenus et programmes éducatifs sur l'IA développer pour les "
                "différents niveaux d'enseignement en Guinée ?</li>"
                "</ol>"
            ),
            'contexte': (
                "L'Afrique, et la Guinée en particulier, se trouve à un carrefour numérique crucial. "
                "La transformation numérique et l'essor de l'intelligence artificielle (IA) offrent un "
                "potentiel immense pour le développement économique et social. Cependant, pour "
                "que la Guinée puisse tirer pleinement parti de cette révolution, il est essentiel de "
                "passer d'une position de consommateur passif à celle d'acteur et de concepteur. "
                "Cela nécessite une stratégie nationale qui reflète les réalités et les priorités "
                "guinéennes, tout en s'inspirant des meilleures pratiques africaines et internationales."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Experts en éducation numérique</strong></li>"
                "<li><strong>Représentants du ministère de l'Éducation</strong></li>"
                "<li><strong>Enseignants et formateurs</strong></li>"
                "<li><strong>Entreprises EdTech</strong></li>"
                "<li><strong>Chercheurs en IA éducationnelle</strong></li>"
                "</ul>"
            ),
        },
        {
            'code': 'SIS',
            'label': "Santé & inclusion sociale",
            'description': "Exploration de l'IA dans la santé : aide au diagnostic, dossiers médicaux numériques et usages éthiques des données.",
            'ordre': 2,
            'objectif': (
                "Cette table ronde explorera comment l'IA peut transformer le secteur de la\n"
                "santé guinéen, en se concentrant sur l'aide au diagnostic médical et l'amélioration de\n"
                "la gestion des dossiers médicaux numériques. Les discussions porteront sur les cas\n"
                "d'usage prometteurs de l'IA pour améliorer le diagnostic, garantir la collecte et\n"
                "l'utilisation éthique des données de santé, et identifier les infrastructures et\n"
                "compétences nécessaires pour déployer des solutions d'IA pertinentes."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Quels sont les cas d'usage les plus prometteurs de l'IA pour améliorer le "
                "diagnostic médical en Guinée aujourd'hui ?</li>"
                "<li>Comment garantir la collecte, le stockage sécurisé et l'utilisation éthique des "
                "données de santé pour alimenter des outils d'IA, tout en respectant la "
                "confidentialité des patients ?</li>"
                "<li>Quelles infrastructures et compétences sont nécessaires pour déployer et "
                "maintenir des solutions d'IA pertinentes dans les structures de santé "
                "guinéennes ?</li>"
                "<li>Quels partenariats peuvent accélérer l'adoption d'outils d'IA bénéfiques pour "
                "la santé en Guinée ?</li>"
                "</ol>"
            ),
            'contexte': (
                "Le secteur de la santé en Guinée fait face à des défis majeurs : manque d'infrastructures "
                "sanitaires, pénurie de personnel qualifié, et difficultés d'accès aux soins. L'intelligence "
                "artificielle offre des opportunités significatives pour améliorer la qualité des soins, "
                "optimiser la gestion des systèmes de santé, et rendre les services plus accessibles."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Professionnels de santé</strong></li>"
                "<li><strong>Experts en santé numérique</strong></li>"
                "<li><strong>Représentants du ministère de la Santé</strong></li>"
                "<li><strong>Fournisseurs de solutions e-santé</strong></li>"
                "<li><strong>Chercheurs en IA médicale</strong></li>"
                "</ul>"
            ),
        },
        {
            'code': 'JSD',
            'label': "Justice, sécurité & défense",
            'description': "Cadres de régulation et enjeux éthiques de l'IA dans la justice, la sécurité et la défense.",
            'ordre': 3,
            'objectif': (
                "Cette table ronde examinera les cadres de régulation, de gouvernance des\n"
                "données et les enjeux éthiques liés à l'adoption de l'IA dans les secteurs de la\n"
                "justice, de la sécurité et de la défense en Guinée. Elle se concentrera sur la définition\n"
                "de stratégies pour maximiser les opportunités offertes par l'IA tout en atténuant les\n"
                "risques spécifiques à ces secteurs, en tenant compte des réalités et priorités\n"
                "nationales."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Quels sont les défis et les opportunités spécifiques liés à l'utilisation de l'IA "
                "dans les systèmes judiciaires, les forces de sécurité et les institutions de "
                "défense en Guinée ?</li>"
                "<li>Comment concevoir des cadres de régulation et de gouvernance des "
                "données qui favorisent l'innovation tout en protégeant les droits et libertés "
                "individuels dans l'utilisation de l'IA ?</li>"
                "<li>Quels principes éthiques devraient guider le développement et le déploiement "
                "de solutions d'IA dans les secteurs de la justice, de la sécurité et de la "
                "défense pour garantir la transparence, la redevabilité et l'équité ?</li>"
                "<li>Comment renforcer les compétences des acteurs de la justice, de la sécurité "
                "et de la défense en matière d'IA et de gestion des données pour assurer une "
                "utilisation responsable et efficace de ces technologies ?</li>"
                "</ol>"
            ),
            'contexte': (
                "Les secteurs de la justice, de la sécurité et de la défense en Guinée sont à un point "
                "d'inflexion. L'émergence de l'IA transforme les méthodes de travail et les capacités "
                "d'analyse, tout en soulevant des enjeux de souveraineté numérique, de protection "
                "des données et d'équilibre entre sécurité et libertés."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Magistrats et juristes</strong></li>"
                "<li><strong>Forces de l'ordre</strong></li>"
                "<li><strong>Militaires et défense</strong></li>"
                "<li><strong>Experts en cybersécurité</strong></li>"
                "<li><strong>Législateurs et décideurs politiques</strong></li>"
                "</ul>"
            ),
        },
        {
            'code': 'RHE',
            'label': "Ressources humaines, gestion d'entreprise & secteur informel",
            'description': "Adoption de l'IA par les startups/PME et structuration de l'écosystème data & IA en Guinée.",
            'ordre': 4,
            'objectif': (
                "Cette table ronde explorera les stratégies pour encourager l'appropriation\n"
                "et l'adoption de l'IA par les startups, les PME et les jeunes innovateurs guinéens. Elle\n"
                "se concentrera sur l'identification des leviers pour renforcer l'écosystème de\n"
                "recherche en sciences de données et IA en Guinée, et sur la co-élaboration de\n"
                "recommandations pour une stratégie nationale structurante en Données Numériques\n"
                "et IA."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Comment l'IA peut-elle stimuler l'innovation et la croissance des startups et "
                "PME en Guinée, et quels sont les secteurs les plus prometteurs pour "
                "l'adoption de ces technologies ?</li>"
                "<li>Quels types de soutien (financier, technique, mentorat) sont les plus efficaces "
                "pour encourager l'adoption de l'IA par les jeunes entrepreneurs et les PME, et "
                "comment les rendre accessibles ?</li>"
                "<li>Comment renforcer les liens entre la recherche en IA et le secteur privé pour "
                "favoriser la création de solutions innovantes adaptées aux besoins du marché "
                "guinéen ?</li>"
                "<li>Quelles politiques publiques (incitations fiscales, réglementations, "
                "programmes de formation) peuvent créer un environnement favorable à "
                "l'émergence d'un écosystème IA dynamique et inclusif en Guinée ?</li>"
                "</ol>"
            ),
            'contexte': (
                "L'écosystème entrepreneurial guinéen dispose d'un potentiel d'innovation important, "
                "mais des contraintes structurelles demeurent. L'IA représente une opportunité pour "
                "accélérer la modernisation de l'économie, créer des emplois qualifiés et renforcer "
                "la compétitivité des entreprises."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Entrepreneurs et startups</strong></li>"
                "<li><strong>PME et grandes entreprises</strong></li>"
                "<li><strong>Incubateurs et accélérateurs</strong></li>"
                "<li><strong>Investisseurs et bailleurs</strong></li>"
                "<li><strong>Experts en transformation numérique</strong></li>"
                "</ul>"
            ),
        },
        {
            'code': 'ADR',
            'label': "Agriculture & développement rural",
            'description': "IA pour moderniser l'agriculture : productivité, durabilité et résilience climatique.",
            'ordre': 5,
            'objectif': (
                "Cette table ronde explorera le potentiel de l'IA pour moderniser le secteur\n"
                "agricole en Guinée, en mettant l'accent sur l'amélioration de la productivité, la\n"
                "promotion de pratiques durables et le renforcement de la résilience face aux défis\n"
                "climatiques. Elle examinera comment l'accès et l'analyse de données pertinentes\n"
                "peuvent optimiser l'allocation des ressources et favoriser une prise de décision\n"
                "basée sur des preuves concrètes dans le secteur agricole."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Comment l'IA peut-elle contribuer à améliorer la productivité agricole en "
                "Guinée, par exemple à travers la surveillance des cultures, l'optimisation de "
                "l'irrigation, la prédiction des rendements et la lutte contre les ravageurs et les "
                "maladies ?</li>"
                "<li>Quelles solutions d'IA peuvent promouvoir des pratiques agricoles durables et "
                "respectueuses de l'environnement, telles que la gestion précise des intrants, "
                "la réduction des émissions de gaz à effet de serre et la conservation des "
                "ressources naturelles ?</li>"
                "<li>Comment l'IA peut-elle renforcer la résilience des systèmes agricoles face aux "
                "chocs climatiques, tels que les sécheresses, les inondations et les "
                "événements météorologiques extrêmes, en permettant une meilleure "
                "anticipation et une adaptation plus efficace ?</li>"
                "<li>Quels sont les défis spécifiques à l'adoption de l'IA dans le secteur agricole "
                "guinéen, et comment les surmonter en termes d'infrastructures, de "
                "compétences, de données et d'accès aux technologies pour les petits "
                "exploitants ?</li>"
                "</ol>"
            ),
            'contexte': (
                "Le secteur agricole représente une part majeure de l'économie guinéenne mais reste "
                "confronté à une faible productivité et à une forte dépendance climatique. L'IA et "
                "l'analyse de données peuvent aider à optimiser les pratiques, améliorer les rendements "
                "et renforcer la sécurité alimentaire."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Agriculteurs et coopératives</strong></li>"
                "<li><strong>Experts agronomes</strong></li>"
                "<li><strong>Fournisseurs de technologies agricoles</strong></li>"
                "<li><strong>Représentants du ministère de l'Agriculture</strong></li>"
                "<li><strong>Chercheurs en IA agricole</strong></li>"
                "</ul>"
            ),
        },
        {
            'code': 'MCB',
            'label': "Mines, environnement, climat & biosphère",
            'description': "IA et données massives pour la gestion des ressources naturelles et l'adaptation au changement climatique.",
            'ordre': 6,
            'objectif': (
                "Cette table ronde examinera comment l'analyse de données massives via\n"
                "l'IA peut aider la Guinée à mieux gérer ses ressources naturelles et à renforcer sa\n"
                "capacité à anticiper et à répondre aux impacts du changement climatique. Les\n"
                "discussions porteront sur l'amélioration du suivi de la déforestation, la gestion des\n"
                "ressources en eau, la surveillance de la biodiversité et le développement de\n"
                "systèmes d'alerte précoce face aux risques climatiques."
            ),
            'questions_cles': (
                "<ol>"
                "<li>Comment l'IA peut-elle améliorer le suivi de la déforestation, la gestion des "
                "ressources en eau, ou la surveillance de la biodiversité en Guinée à partir des "
                "données disponibles ?</li>"
                "<li>Quelles applications de l'IA peuvent aider à développer des systèmes d'alerte "
                "précoce plus efficaces face aux risques climatiques ?</li>"
                "<li>Quels sont les défis liés à l'accès, la qualité et le partage des données "
                "environnementales nécessaires pour entraîner des modèles d'IA pertinents en "
                "Guinée ?</li>"
                "<li>Comment intégrer les outils d'IA dans les stratégies nationales d'adaptation et "
                "d'atténuation du changement climatique et de protection de l'environnement ?</li>"
                "</ol>"
            ),
            'contexte': (
                "La Guinée dispose d'un patrimoine naturel important mais la gestion durable de ces "
                "ressources face au changement climatique nécessite des outils avancés. L'IA peut "
                "renforcer la surveillance environnementale, l'optimisation des ressources et "
                "l'anticipation des risques."
            ),
            'intervenants': (
                "<ul>"
                "<li><strong>Experts environnementaux</strong></li>"
                "<li><strong>Géologues et miniers</strong></li>"
                "<li><strong>Représentants du ministère de l'Environnement</strong></li>"
                "<li><strong>Chercheurs en climatologie</strong></li>"
                "<li><strong>Fournisseurs de solutions environnementales</strong></li>"
                "</ul>"
            ),
        },
    ]

    for data in ateliers:
        obj, created = Atelier.objects.get_or_create(
            code=data['code'],
            defaults={
                'label': data['label'],
                'description': data['description'],
                'ordre': data['ordre'],
                'active': True,
            },
        )

        update_fields = []
        for field in ['label', 'description', 'ordre', 'active', 'objectif', 'questions_cles', 'contexte', 'intervenants']:
            if hasattr(obj, field):
                new_value = data.get(field)
                if new_value is not None and getattr(obj, field) != new_value:
                    setattr(obj, field, new_value)
                    update_fields.append(field)

        if update_fields:
            obj.save(update_fields=update_fields)


def unseed_atelier_details(apps, schema_editor):
    Atelier = apps.get_model('inscriptions', 'Atelier')
    Atelier.objects.filter(code__in=['EESR', 'SIS', 'JSD', 'RHE', 'ADR', 'MCB']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('inscriptions', '0033_atelier_contexte_atelier_intervenants_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_atelier_details, reverse_code=unseed_atelier_details),
    ]
