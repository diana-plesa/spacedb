"""
Custom template filters. Use in a template with  {% load space_format %}
"""
from django import template

register = template.Library()

SUPERSCRIPT_DIGITS = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


@register.filter
def sci(value):
    """
    Writes very big numbers in scientific notation so they fit on the page:
        4000000000000 -> '4 × 10¹²'      6500000000 -> '6.5 × 10⁹'
    Numbers under ten million keep thousands separators:
        2537000 -> '2,537,000'           4.37 -> '4.37'
    """
    if value is None or value == '':
        return '—'
    value = float(value)
    if abs(value) < 1e7:
        return f'{value:,.3f}'.rstrip('0').rstrip('.')
    mantissa, exponent = f'{value:.2e}'.split('e')  # '4.00', '+12'
    mantissa = mantissa.rstrip('0').rstrip('.')
    return f'{mantissa} × 10{str(int(exponent)).translate(SUPERSCRIPT_DIGITS)}'
