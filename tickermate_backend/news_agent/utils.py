from datetime import datetime, timezone
import re

def clean_gpt_text(text):
    if not text:
        return ""
    return re.sub(r'^[\W_"\']+|[\W_"\']+$', '', text.strip())

def time_diff_calc(publish_at):
    publish_at = publish_at.replace(tzinfo = timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - publish_at

    minutes = diff.total_seconds() // 60
    hours = diff.total_seconds() // 3600
    days = diff.total_seconds() // (3600*24)

    if minutes < 1:
        return "Just now"
    elif minutes < 60:
        return f"{int(minutes)}m ago"
    elif hours < 24:
        return f"{int(hours)}h ago"
    elif days < 7:
        return f"{int(days)}d ago"
    else:
        return publish_at.strftime("%Y-%m-%d")

def get_time_diff(publish_at_str):
    from datetime import datetime

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",      # NewsAPI
        "%Y-%m-%dT%H:%M:%S.%fZ"    # Marketaux
    ]

    for fmt in formats:
        try:
            publish_at = datetime.strptime(publish_at_str, fmt)
            return time_diff_calc(publish_at)
        except ValueError:
            continue

    return "Unknown Time"

def parse_published_time(iso_str):
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc)
    except:
        return datetime.min.replace(tzinfo=timezone.utc)