from datetime import datetime, timezone
import re

def clean_gpt_text(text):
    if not text:
        return ""
    return re.sub(r'^[^\w(]*|[^\w).?!"]*$', '', text.strip())


def get_time_diff(publish_at_str):
    try:
        publish_at = datetime.strptime(publish_at_str,"%Y-%m-%dT%H:%M:%SZ")
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
    except:
        return "Unknown Time"

def parse_published_time(iso_str):
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc)
    except:
        return datetime.min.replace(tzinfo=timezone.utc)