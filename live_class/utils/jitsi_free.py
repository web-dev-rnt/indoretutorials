# live_class/utils/jitsi_free.py
import hashlib
from django.conf import settings

def generate_room_name(session_id, class_name):
    """Generate one stable, hard-to-guess room name for a saved session."""
    unique_string = f"{settings.SECRET_KEY}:{session_id}:{class_name}"
    room_hash = hashlib.sha256(unique_string.encode()).hexdigest()[:24]
    return f"EduTrellisLiveClass{room_hash}"

def is_room_moderator(user):
    """Determine if user should be a moderator"""
    # You can customize this logic based on your requirements
    # For example: staff users, course instructors, etc.
    return user.is_staff or user.is_superuser

def get_jitsi_config(room_name, display_name, is_moderator, user_email):
    """Get Jitsi configuration for the room"""
    config = {
        'roomName': room_name,
        'displayName': display_name,
        'email': user_email,
        'startWithAudioMuted': not is_moderator,
        'startWithVideoMuted': not is_moderator,
        'enableWelcomePage': False,
        'prejoinPageEnabled': False,
        'requireDisplayName': True,
    }
    
    if is_moderator:
        config.update({
            'moderator': True,
            'startWithAudioMuted': False,
            'startWithVideoMuted': False,
        })
    
    return config
