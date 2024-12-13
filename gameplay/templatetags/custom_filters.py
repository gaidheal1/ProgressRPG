from django import template

register = template.Library()

@register.filter
def format_duration(seconds):
    """Convert seconds to HH:MM:SS format."""
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:2}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:2}:{seconds:02}"
    except (ValueError, TypeError):
        return "00:00"