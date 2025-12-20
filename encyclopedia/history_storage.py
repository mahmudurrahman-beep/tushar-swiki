import json
import os
from django.conf import settings
from pathlib import Path

def get_history_file(title):
    """Get path to history JSON file for a page"""
    history_dir = Path(settings.BASE_DIR) / 'history'
    history_dir.mkdir(exist_ok=True)
    return history_dir / f"{title}.json"

def save_to_history(title, user, content):
    """Save edit to file-based history"""
    history_file = get_history_file(title)
    
    # Load existing history
    history = []
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    # Add new entry
    history.append({
        'user': user.username if user else 'Anonymous',
        'user_id': user.id if user else None,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 10 edits
    if len(history) > 10:
        history = history[-10:]
    
    # Save back
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    return history

def load_from_history(title):
    """Load edit history from file"""
    history_file = get_history_file(title)
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f)
    return []
