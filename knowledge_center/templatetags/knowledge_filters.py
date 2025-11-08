from django import template
from django.utils import timezone

register = template.Library()

HEBREW_MONTHS = {
    1: 'ינואר',
    2: 'פברואר',
    3: 'מרץ',
    4: 'אפריל',
    5: 'מאי',
    6: 'יוני',
    7: 'יולי',
    8: 'אוגוסט',
    9: 'ספטמבר',
    10: 'אוקטובר',
    11: 'נובמבר',
    12: 'דצמבר',
}

@register.filter
def hebrew_datetime(value):
    """
    Convert datetime to Hebrew format: "יום חודש שנה, שעה:דקה"
    Example: "28 אוקטובר 2025, 15:30"
    """
    if not value:
        return ''

    # Ensure we're working with a timezone-aware datetime
    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    # Get local time
    local_time = timezone.localtime(value)

    day = local_time.day
    month = HEBREW_MONTHS.get(local_time.month, '')
    year = local_time.year
    hour = local_time.strftime('%H')
    minute = local_time.strftime('%M')

    return f"{day} {month} {year}, {hour}:{minute}"
