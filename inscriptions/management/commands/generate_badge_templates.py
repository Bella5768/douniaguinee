"""
Commande Django pour générer les templates PNG de badges par catégorie.
Crée des badges 591x1004 px avec fond coloré, titre de catégorie, date, et zones réservées.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


CATEGORIES = {
    'vip': {
        'label': 'VIP TOUT ACCÈS',
        'bg_color': '#003366',
        'accent_color': '#FFD700',
    },
    'grand_public': {
        'label': 'GRAND PUBLIC',
        'bg_color': '#1a6b3c',
        'accent_color': '#FFFFFF',
    },
    'speaker': {
        'label': 'SPEAKER',
        'bg_color': '#8B0000',
        'accent_color': '#FFD700',
    },
    'sponsor': {
        'label': 'SPONSOR',
        'bg_color': '#4B0082',
        'accent_color': '#FFD700',
    },
    'presse': {
        'label': 'PRESSE',
        'bg_color': '#CC5500',
        'accent_color': '#FFFFFF',
    },
    'staff': {
        'label': 'STAFF',
        'bg_color': '#2F4F4F',
        'accent_color': '#00CED1',
    },
    'organisateur': {
        'label': 'ORGANISATEUR',
        'bg_color': '#191970',
        'accent_color': '#FFD700',
    },
}

WIDTH, HEIGHT = 591, 1004


def _get_font(size, bold=True):
    """Charge une police système."""
    names = ['arialbd.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf', 'DejaVuSans.ttf'] if bold else ['arial.ttf', 'DejaVuSans.ttf']
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generate_template(cat_key, cat_info, output_dir):
    """Génère un template PNG pour une catégorie donnée."""
    img = Image.new('RGB', (WIDTH, HEIGHT), cat_info['bg_color'])
    draw = ImageDraw.Draw(img)

    # --- En-tête : logo texte DounIA ---
    font_logo = _get_font(42)
    logo_text = "DounIA"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    logo_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - logo_w) // 2, 40), logo_text, fill='#FFFFFF', font=font_logo)

    # --- Sous-titre : Conférence Nationale ---
    font_sub = _get_font(18, bold=False)
    sub_text = "Conférence Nationale"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - sub_w) // 2, 100), sub_text, fill='#CCCCCC', font=font_sub)

    # --- Ligne de séparation ---
    draw.line([(50, 140), (WIDTH - 50, 140)], fill=cat_info['accent_color'], width=2)

    # --- Photo placeholder (cercle) ---
    circle_cx, circle_cy, circle_r = WIDTH // 2, 260, 80
    draw.ellipse(
        [circle_cx - circle_r, circle_cy - circle_r, circle_cx + circle_r, circle_cy + circle_r],
        fill='#555555', outline='#FFFFFF', width=3,
    )
    font_photo = _get_font(14, bold=False)
    ph_text = "PHOTO"
    bbox = draw.textbbox((0, 0), ph_text, font=font_photo)
    ph_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - ph_w) // 2, circle_cy - 8), ph_text, fill='#AAAAAA', font=font_photo)

    # --- Catégorie (label central, couleur accent) ---
    font_cat = _get_font(36)
    cat_text = cat_info['label']
    bbox = draw.textbbox((0, 0), cat_text, font=font_cat)
    cat_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - cat_w) // 2, 380), cat_text, fill=cat_info['accent_color'], font=font_cat)

    # --- Ligne de séparation ---
    draw.line([(80, 440), (WIDTH - 80, 440)], fill=cat_info['accent_color'], width=1)

    # --- Labels "Nom" et "Prénoms :" ---
    font_label = _get_font(20, bold=False)
    draw.text((60, 500), "Nom :", fill='#AAAAAA', font=font_label)
    draw.text((60, 600), "Prénoms :", fill='#AAAAAA', font=font_label)

    # --- Zones de texte (le texte sera ajouté dynamiquement) ---
    # Nom : y=555, Prénoms : y=655
    # Ligne fine sous chaque zone
    draw.line([(60, 590), (WIDTH - 60, 590)], fill='#444444', width=1)
    draw.line([(60, 690), (WIDTH - 60, 690)], fill='#444444', width=1)

    # --- Date ---
    font_date = _get_font(16, bold=False)
    date_text = "15 Août 2026 — Conakry, Guinée"
    bbox = draw.textbbox((0, 0), date_text, font=font_date)
    date_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - date_w) // 2, 720), date_text, fill='#CCCCCC', font=font_date)

    # --- Zone QR code (carré blanc) ---
    qr_x1, qr_y1, qr_x2, qr_y2 = 231, 791, 394, 954
    draw.rectangle([qr_x1, qr_y1, qr_x2, qr_y2], fill='#FFFFFF')

    # --- Pied de page ---
    font_footer = _get_font(12, bold=False)
    footer_text = "dounia.org"
    bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    ft_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - ft_w) // 2, HEIGHT - 35), footer_text, fill='#888888', font=font_footer)

    # --- Sauvegarder ---
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"badge_{cat_key}.png")
    img.save(filepath, 'PNG')
    return filepath


class Command(BaseCommand):
    help = 'Génère les templates PNG de badges pour toutes les catégories de la conférence.'

    def handle(self, *args, **options):
        output_dir = os.path.join(settings.BASE_DIR, 'static', 'badges', 'badges_templates')
        self.stdout.write(f"Génération des templates dans : {output_dir}")

        for cat_key, cat_info in CATEGORIES.items():
            path = generate_template(cat_key, cat_info, output_dir)
            self.stdout.write(self.style.SUCCESS(f"  ✓ {cat_key} → {path}"))

        self.stdout.write(self.style.SUCCESS(f"\n{len(CATEGORIES)} templates générés avec succès."))
