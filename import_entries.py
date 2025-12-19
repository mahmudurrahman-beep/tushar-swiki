"""
Import script for wiki entries.
Optimized for Render.com deployment with filesystem fallback.
"""

import os
import sys
import django
from pathlib import Path
import shutil

# ====== SETUP DJANGO ======
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki.settings')
django.setup()

# ====== IMPORTS ======
from encyclopedia.util import save_entry, get_entry, list_entries, ensure_entries_directory
from encyclopedia.models import Entry
from django.contrib.auth.models import User
from django.conf import settings

# ====== SAMPLE ENTRIES (fallback if no .md files) ======
SAMPLE_ENTRIES = [
    ("CSS", """# CSS

Cascading Style Sheets (CSS) is a style sheet language used for describing the presentation of a document written in HTML or XML.

## Key Features
- Separates content from presentation
- Supports responsive design
- Works with all modern browsers

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}
```"""),
    
    ("Django", """# Django

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.

## Features
- Batteries-included framework
- Excellent documentation
- Built-in admin interface
- ORM (Object-Relational Mapping)
- Security features out of the box

## Basic Setup
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```"""),
    
    ("Git", """# Git

Git is a distributed version control system that tracks changes in source code during software development.

## Basic Commands
```bash
git init          # Initialize repository
git add .         # Stage all changes
git commit -m "message"  # Commit changes
git push origin main     # Push to remote
git pull          # Pull latest changes
