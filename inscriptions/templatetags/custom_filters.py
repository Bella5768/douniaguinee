from django import template
import re
from django.utils.safestring import mark_safe

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


@register.filter
def dounia_exposant(value):
    value = str(value or '')

    def _repl(m):
        return f"DounIA<sup>{m.group(1)}</sup>"

    value = re.sub(r"DounIA\s*([12])", _repl, value)
    return mark_safe(value)
