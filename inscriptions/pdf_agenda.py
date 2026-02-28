import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


PRIMARY = HexColor('#1B3A5C')
PRIMARY_LIGHT = HexColor('#2A5A8C')
PRIMARY_DARK = HexColor('#0F2340')
ACCENT = HexColor('#003366')
WHITE = HexColor('#FFFFFF')
LIGHT_BG = HexColor('#F7F8FA')
TEXT_DARK = HexColor('#1A1A2E')
TEXT_MUTED = HexColor('#5A6270')
BORDER = HexColor('#DEE2E6')

AGENDA_ATELIERS = {
    'education': {
        'titre': 'Éducation, enseignement supérieur, recherche & innovation',
        'icone': 'Atelier 1',
        'frequence': '2 sessions / semaine',
        'horaire': '9h00 – 12h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Hybride',
        'public': 'Chercheurs, enseignants, étudiants',
        'objectifs': [
            'Analyser l\'impact de l\'IA sur les systèmes éducatifs guinéens',
            'Identifier les opportunités d\'innovation dans la recherche',
            'Proposer un cadre pour l\'intégration de l\'IA dans l\'enseignement supérieur',
            'Élaborer des recommandations pour la formation aux compétences numériques',
        ],
    },
    'sante': {
        'titre': 'Santé & inclusion sociale',
        'icone': 'Atelier 2',
        'frequence': '2 sessions / semaine',
        'horaire': '14h00 – 17h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Hybride',
        'public': 'Professionnels santé, ONG',
        'objectifs': [
            'Explorer les applications de l\'IA pour améliorer l\'accès aux soins',
            'Étudier les solutions IA pour le diagnostic médical en zones rurales',
            'Renforcer l\'inclusion sociale grâce aux technologies numériques',
            'Proposer un cadre éthique pour l\'utilisation de l\'IA en santé',
        ],
    },
    'justice': {
        'titre': 'Justice, sécurité & défense',
        'icone': 'Atelier 3',
        'frequence': '2 sessions / semaine',
        'horaire': '9h00 – 12h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Présentiel + distanciel',
        'public': 'Juristes, institutions',
        'objectifs': [
            'Définir un cadre éthique et juridique pour l\'IA dans la justice',
            'Analyser les enjeux sécuritaires liés à l\'utilisation de l\'IA',
            'Étudier les bonnes pratiques internationales en matière de défense numérique',
            'Proposer des recommandations pour une gouvernance responsable',
        ],
    },
    'rh_entreprise': {
        'titre': 'Ressources humaines, gestion d\'entreprise & secteur informel',
        'icone': 'Atelier 4',
        'frequence': '2 sessions / semaine',
        'horaire': '14h00 – 17h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Hybride',
        'public': 'Entreprises, startups, PME',
        'objectifs': [
            'Moderniser la gestion des ressources humaines grâce à l\'IA',
            'Accompagner la transformation digitale des entreprises guinéennes',
            'Proposer des outils pour la formalisation du secteur informel',
            'Stimuler l\'entrepreneuriat technologique en Guinée',
        ],
    },
    'agriculture': {
        'titre': 'Agriculture & développement rural',
        'icone': 'Atelier 5',
        'frequence': '2 sessions / semaine',
        'horaire': '9h00 – 12h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Hybride',
        'public': 'Agriculteurs, chercheurs, ONG',
        'objectifs': [
            'Développer l\'agriculture de précision adaptée au contexte guinéen',
            'Renforcer la sécurité alimentaire grâce aux données et à l\'IA',
            'Proposer des solutions numériques pour le développement rural',
            'Créer des synergies entre recherche agronomique et technologies',
        ],
    },
    'mines_env': {
        'titre': 'Mines, environnement, climat & biosphère',
        'icone': 'Atelier 6',
        'frequence': '2 sessions / semaine',
        'horaire': '14h00 – 17h00 (GMT)',
        'duree': '4 semaines',
        'format': 'Hybride',
        'public': 'Experts mines, environnement',
        'objectifs': [
            'Optimiser la gestion des ressources minières par l\'IA',
            'Surveiller et protéger l\'environnement grâce aux données satellitaires',
            'Lutter contre les effets du changement climatique avec des outils numériques',
            'Préserver la biodiversité et la biosphère guinéenne',
        ],
    },
}


def generer_agenda_pdf(inscription):
    """Génère un PDF professionnel de l'agenda de l'atelier pour un inscrit."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    style_header = ParagraphStyle(
        'Header', parent=styles['Title'],
        fontSize=22, textColor=PRIMARY, spaceAfter=4 * mm,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontSize=11, textColor=TEXT_MUTED, alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    style_section = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        fontSize=14, textColor=PRIMARY, fontName='Helvetica-Bold',
        spaceBefore=8 * mm, spaceAfter=4 * mm,
    )
    style_body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, textColor=TEXT_DARK, leading=16,
        spaceAfter=2 * mm,
    )
    style_small = ParagraphStyle(
        'Small', parent=styles['Normal'],
        fontSize=9, textColor=TEXT_MUTED, leading=14,
    )
    style_bullet = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontSize=10, textColor=TEXT_DARK, leading=16,
        leftIndent=10 * mm, bulletIndent=4 * mm,
        spaceAfter=2 * mm,
    )
    style_footer = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER,
        spaceBefore=10 * mm,
    )

    agenda = AGENDA_ATELIERS.get(inscription.atelier, {})
    if not agenda:
        return None

    elements = []

    # Header
    elements.append(Paragraph("DounIA 2", style_header))
    elements.append(Paragraph(
        "Données Numériques & Intelligence Artificielle — Guinée",
        style_subtitle
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=ACCENT,
        spaceAfter=8 * mm, spaceBefore=2 * mm,
    ))

    # Destinataire
    elements.append(Paragraph("AGENDA PERSONNEL", style_section))
    elements.append(Paragraph(
        f"Préparé pour : <b>{inscription.prenom} {inscription.nom}</b>",
        style_body
    ))
    elements.append(Paragraph(
        f"Institution : {inscription.institution} — {inscription.fonction}",
        style_small
    ))
    elements.append(Spacer(1, 6 * mm))

    # Atelier info table
    elements.append(Paragraph("DÉTAILS DE L'ATELIER", style_section))
    elements.append(Paragraph(
        f"<b>{agenda['titre']}</b>",
        ParagraphStyle('AtelierTitre', parent=style_body, fontSize=12, textColor=PRIMARY)
    ))
    elements.append(Spacer(1, 4 * mm))

    table_data = [
        [Paragraph("<b>Période</b>", style_small), Paragraph("Octobre 2026", style_body)],
        [Paragraph("<b>Fréquence</b>", style_small), Paragraph(agenda['frequence'], style_body)],
        [Paragraph("<b>Horaire</b>", style_small), Paragraph(agenda['horaire'], style_body)],
        [Paragraph("<b>Durée totale</b>", style_small), Paragraph(agenda['duree'], style_body)],
        [Paragraph("<b>Format</b>", style_small), Paragraph(agenda['format'], style_body)],
        [Paragraph("<b>Public cible</b>", style_small), Paragraph(agenda['public'], style_body)],
    ]

    table = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_DARK),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6 * mm))

    # Objectifs
    elements.append(Paragraph("OBJECTIFS DE L'ATELIER", style_section))
    for obj in agenda.get('objectifs', []):
        elements.append(Paragraph(
            f"• {obj}",
            style_bullet
        ))
    elements.append(Spacer(1, 6 * mm))

    # Programme prévisionnel
    elements.append(Paragraph("PROGRAMME PRÉVISIONNEL", style_section))
    programme_data = [
        [
            Paragraph("<b>Semaine</b>", ParagraphStyle('TH', parent=style_small, textColor=WHITE)),
            Paragraph("<b>Thème</b>", ParagraphStyle('TH', parent=style_small, textColor=WHITE)),
            Paragraph("<b>Format</b>", ParagraphStyle('TH', parent=style_small, textColor=WHITE)),
        ],
        [Paragraph("Semaine 1", style_body), Paragraph("Introduction, état des lieux et diagnostic sectoriel", style_body), Paragraph("Plénière", style_body)],
        [Paragraph("Semaine 2", style_body), Paragraph("Analyse approfondie et études de cas", style_body), Paragraph("Groupes de travail", style_body)],
        [Paragraph("Semaine 3", style_body), Paragraph("Co-construction des recommandations", style_body), Paragraph("Ateliers pratiques", style_body)],
        [Paragraph("Semaine 4", style_body), Paragraph("Synthèse, feuille de route et restitution", style_body), Paragraph("Plénière finale", style_body)],
    ]

    prog_table = Table(programme_data, colWidths=[3.5 * cm, 8.5 * cm, 3.5 * cm])
    prog_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BACKGROUND', (0, 1), (-1, -1), WHITE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(prog_table)
    elements.append(Spacer(1, 8 * mm))

    # Infos pratiques
    elements.append(Paragraph("INFORMATIONS PRATIQUES", style_section))
    elements.append(Paragraph(
        "• Les détails logistiques (lieu exact, liens de connexion) seront communiqués "
        "par email une semaine avant le début de l'atelier.",
        style_bullet
    ))
    elements.append(Paragraph(
        "• Chaque participant recevra un kit de documentation avant la première session.",
        style_bullet
    ))
    elements.append(Paragraph(
        "• Un certificat de participation sera délivré à l'issue de l'atelier.",
        style_bullet
    ))
    elements.append(Spacer(1, 6 * mm))

    # Votre engagement
    elements.append(Paragraph("VOTRE ENGAGEMENT", style_section))
    elements.append(Paragraph(
        f"Type d'engagement : <b>{inscription.get_engagement_display()}</b>",
        style_body
    ))
    elements.append(Paragraph(
        f"Format préféré : <b>{inscription.get_format_preference_display()}</b>",
        style_body
    ))
    elements.append(Paragraph(
        f"Disponibilité : <b>{inscription.get_disponibilite_display()}</b>",
        style_body
    ))

    # Footer
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=BORDER,
        spaceAfter=4 * mm, spaceBefore=4 * mm,
    ))
    elements.append(Paragraph(
        "DounIA — Données Numériques & Intelligence Artificielle<br/>"
        "Contact : contact@dounia.gn | Conakry, Guinée<br/>"
        "© 2026 DounIA — Tous droits réservés",
        style_footer
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
