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


@register.filter
def strip_trailing_dash(value):
    s = str(value or '')
    s = s.rstrip()
    if s.endswith('—'):
        s = s[:-1].rstrip()
    if s.endswith('-'):
        s = s[:-1].rstrip()
    return s


@register.filter
def strip_leading_dash(value):
    s = str(value or '')
    s = s.lstrip()
    if s.startswith('—'):
        s = s[1:].lstrip()
    if s.startswith('-'):
        s = s[1:].lstrip()
    return s
