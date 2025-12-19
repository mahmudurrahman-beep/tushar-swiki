#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Setting up database..."
python manage.py migrate

echo "📁 Creating entries directory..."
# Create entries folder for your util.py functions
mkdir -p entries

echo "📝 Creating sample markdown files..."
# Create sample .md files if none exist
if [ ! -f "entries/CSS.md" ]; then
    echo "# CSS\n\nCascading Style Sheets is a style sheet language." > entries/CSS.md
    echo "# Django\n\nDjango is a high-level Python web framework." > entries/Django.md
    echo "# Git\n\nGit is a distributed version control system." > entries/Git.md
    echo "# HTML\n\nHTML is the standard markup language." > entries/HTML.md
    echo "# Python\n\nPython is a programming language." > entries/Python.md
    echo "# Generative AI\n\nGenerative AI creates new content." > entries/Generative\ AI.md
    echo "Created 6 sample markdown files"
fi

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "📚 Importing entries..."
python import_entries.py

echo "✅ Build completed!"
