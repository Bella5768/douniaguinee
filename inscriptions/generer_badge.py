"""
Module de génération de badges PDF pour la conférence DounIA.

Utilise Pillow pour la manipulation d'image, qrcode pour le QR code,
et reportlab pour la conversion en PDF.

Les templates de badges sont uploadés par l'admin via le modèle BadgeTemplate.
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from django.conf import settings


# Répertoire de sortie des badges générés
BADGES_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'badges')


def _parse_color(color, fallback='#FFFFFF'):
    """Convertit une couleur en tuple RGB valide pour Pillow."""
    if not color:
        return fallback
    color = str(color).strip()
    # Si c'est un code hexadécimal #XXX ou #XXXXXX
    if color.startswith('#'):
        color = color[1:]
        if len(color) == 3:
            color = ''.join([c * 2 for c in color])
        if len(color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color):
            return f'#{color.upper()}'
    # Si c'est un nom de couleur connu (ex: white, black)
    try:
        from PIL import ImageColor
        return ImageColor.getcolor(color, 'RGB')
    except (ValueError, AttributeError):
        pass
    return fallback


def _get_font(font_size):
    """Charge une police TTF (système ou embarquée)."""
    # Police embarquée dans le projet
    font_path = os.path.join(settings.BASE_DIR, 'static', 'badges', 'fonts', 'badge_font.ttf')
    try:
        return ImageFont.truetype(font_path, font_size)
    except (IOError, OSError):
        pass
    # Fallback : police système
    for name in ['arialbd.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf']:
        try:
            return ImageFont.truetype(name, font_size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generer_badge(nom, prenom, categorie, identifiant):
    """
    Génère un badge PDF personnalisé pour un participant.

    Charge le template depuis le modèle BadgeTemplate (uploadé par l'admin).

    Args:
        nom (str): Nom de famille du participant (ex: "DIALLO")
        prenom (str): Prénom(s) du participant (ex: "Mamadou")
        categorie (str): Catégorie du participant (ex: "vip", "grand_public")
        identifiant (str): Identifiant unique d'inscription

    Returns:
        str: Chemin absolu du fichier PDF généré

    Raises:
        ValueError: Si aucun template n'est configuré pour cette catégorie.
    """
    from .models import BadgeTemplate

    # 1. Charger le template uploadé pour cette catégorie
    cat_key = categorie.lower().strip()
    try:
        badge_tpl = BadgeTemplate.objects.get(categorie=cat_key)
    except BadgeTemplate.DoesNotExist:
        raise ValueError(
            f"Aucun template de badge uploadé pour la catégorie '{categorie}'. "
            f"Veuillez uploader un template dans Gestion > Conférence."
        )

    template_path = badge_tpl.template_image.path
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template de badge introuvable : {template_path}")

    # 2. Ouvrir le template et dessiner
    badge_img = Image.open(template_path).convert('RGBA')
    draw = ImageDraw.Draw(badge_img)

    # 3. Écrire le nom
    font_nom = _get_font(badge_tpl.nom_font_size)
    draw.text(
        (badge_tpl.nom_x, badge_tpl.nom_y),
        nom.upper(),
        fill=_parse_color(badge_tpl.nom_color),
        font=font_nom,
    )

    # 4. Écrire le prénom
    font_prenom = _get_font(badge_tpl.prenom_font_size)
    draw.text(
        (badge_tpl.prenom_x, badge_tpl.prenom_y),
        prenom,
        fill=_parse_color(badge_tpl.prenom_color),
        font=font_prenom,
    )

    # 5. Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(identifiant)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    # 6. Redimensionner le QR code pour remplir la zone réservée
    qr_width = badge_tpl.qr_x2 - badge_tpl.qr_x1
    qr_height = badge_tpl.qr_y2 - badge_tpl.qr_y1
    qr_img = qr_img.resize((qr_width, qr_height), Image.LANCZOS)

    # 7. Coller le QR code sur le badge
    badge_img.paste(qr_img, (badge_tpl.qr_x1, badge_tpl.qr_y1), qr_img)

    # 8. Créer le répertoire de sortie
    os.makedirs(BADGES_OUTPUT_DIR, exist_ok=True)

    # 9. Sauvegarder l'image composite temporaire
    img_filename = f"badge_{identifiant}.png"
    img_path = os.path.join(BADGES_OUTPUT_DIR, img_filename)
    badge_rgb = badge_img.convert('RGB')
    badge_rgb.save(img_path, 'PNG')

    # 10. Convertir en PDF avec ReportLab
    pdf_filename = f"badge_{identifiant}.pdf"
    pdf_path = os.path.join(BADGES_OUTPUT_DIR, pdf_filename)

    img_w_px, img_h_px = badge_rgb.size
    badge_w_mm = 100  # 10 cm
    badge_h_mm = badge_w_mm * img_h_px / img_w_px

    c = pdf_canvas.Canvas(pdf_path, pagesize=(badge_w_mm * mm, badge_h_mm * mm))
    c.drawImage(img_path, 0, 0, width=badge_w_mm * mm, height=badge_h_mm * mm)
    c.showPage()
    c.save()

    # 11. Nettoyer l'image temporaire PNG
    try:
        os.remove(img_path)
    except OSError:
        pass

    return pdf_path
