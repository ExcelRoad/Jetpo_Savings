"""
Custom template filters for fund display
"""
from django import template

register = template.Library()


@register.filter
def hebrew_period(period):
    """
    Convert YYYYMM period format to Hebrew month name with year.
    Example: 202508 -> "אוגוסט 2025"
    """
    if not period:
        return "—"

    period_str = str(period)
    if len(period_str) != 6:
        return period_str

    year = period_str[:4]
    month = period_str[4:6]

    # Hebrew month names
    hebrew_months = {
        '01': 'ינואר',
        '02': 'פברואר',
        '03': 'מרץ',
        '04': 'אפריל',
        '05': 'מאי',
        '06': 'יוני',
        '07': 'יולי',
        '08': 'אוגוסט',
        '09': 'ספטמבר',
        '10': 'אוקטובר',
        '11': 'נובמבר',
        '12': 'דצמבר',
    }

    month_name = hebrew_months.get(month, month)
    return f"{month_name} {year}"
