from django import template
import re

register = template.Library()

@register.filter
def slugify(value):
    """
    Convertit une chaîne de caractères en slug (URL-friendly)
    """
    value = str(value)
    # Remplacer les caractères non alphanumériques par des tirets
    value = re.sub(r'[^\w\s-]', '', value)
    # Remplacer les espaces et tirets multiples par un seul tiret
    value = re.sub(r'[-\s]+', '-', value)
    # Mettre en minuscules
    return value.strip().lower()
