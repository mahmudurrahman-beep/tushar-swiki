from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Entry
import markdown2
import random
import re

# ============ AUTHENTICATION VIEWS ============

def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not username or not password:
            messages.error(request, "Username and password are required")
        elif len(username) < 3:
            messages.error(request, "Username must be at least 3 characters")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email if email else ''
            )
            login(request, user)
            messages.success(request, f"Welcome, {username}! You can now create and edit pages.")
            return redirect('index')
    
    return render(request, 'encyclopedia/register.html', {'user': request.user})

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'encyclopedia/login.html', {'user': request.user})

def logout_view(request):
    """User logout"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('index')

# ============ WIKI VIEWS ============

def index(request):
    """Home page showing UNIQUE entry titles"""
    # Get all distinct titles, ordered alphabetically
    titles = Entry.objects.values_list('title', flat=True).distinct().order_by('title')
    
    return render(request, 'encyclopedia/index.html', {
        'entries': list(titles),  # Convert QuerySet to list
        'user': request.user
    })

def entry(request, title):
    """Display individual entry (public access)"""
    # Get the most recent entry with this title
    try:
        entry_obj = Entry.objects.filter(title=title).order_by('-created_at').first()
    except Entry.DoesNotExist:
        entry_obj = None
    
    if entry_obj is None:
        return render(request, 'encyclopedia/error.html', {
            'message': f"The page '{title}' was not found.",
            'user': request.user
        }, status=404)
    
    # Convert markdown to HTML
    content_html = markdown2.markdown(entry_obj.content)
    
    # Remove duplicate H1 if it matches the title
    title_pattern = f'<h1[^>]*>\\s*{re.escape(entry_obj.title)}\\s*</h1>'
    content_html = re.sub(title_pattern, '', content_html, flags=re.IGNORECASE)
    
    # Remove any remaining empty H1 at the beginning
    content_html = re.sub(r'^\s*<h1[^>]*>.*?</h1>\s*', '', content_html)
    
    # Get edit history for this page
    edit_history = Entry.objects.filter(title=title).order_by('-created_at')[:5]
    
    return render(request, 'encyclopedia/entry.html', {
        'title': entry_obj.title,
        'content': content_html,
        'entry_obj': entry_obj,
        'entry_user': entry_obj.user,  # Original creator
        'edit_history': edit_history,
        'total_edits': Entry.objects.filter(title=title).count(),
        'user': request.user
    })

def search(request):
    """Search UNIQUE entries"""
    query = request.GET.get('q', '').strip()
    
    # Get unique titles for search
    all_titles = Entry.objects.values_list('title', flat=True).distinct()
    
    if not query:
        return render(request, 'encyclopedia/search.html', {
            'query': query,
            'results': [],
            'user': request.user
        })
    
    # Case-insensitive search on unique titles
    query_lower = query.lower()
    results = [title for title in all_titles if query_lower in title.lower()]
    
    return render(request, 'encyclopedia/search.html', {
        'query': query,
        'results': results,
        'user': request.user
    })

@login_required
def edit_page(request, title):
    """Edit ANY existing page (any authenticated user can edit)"""
    # Get the most recent version
    latest_entry = Entry.objects.filter(title=title).order_by('-created_at').first()
    
    if latest_entry is None:
        # Page doesn't exist yet, redirect to create
        messages.info(request, f"Page '{title}' doesn't exist yet. Create it now!")
        return redirect('new_page')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, "Content cannot be empty")
            return render(request, 'encyclopedia/edit.html', {
                'title': title,
                'content': latest_entry.content if latest_entry else "",
                'user': request.user
            })
        
        # Create NEW version with current user as editor
        new_entry = Entry.objects.create(
            title=title,
            content=content,
            user=request.user  # Current editor
        )
        
        # Track who edited what (optional)
        if latest_entry and latest_entry.user != request.user:
            messages.info(request, 
                f"You've edited '{title}', originally created by {latest_entry.user.username}."
            )
        else:
            messages.success(request, f"Page '{title}' updated successfully!")
        
        return redirect('entry', title=title)
    
    # Pre-fill with latest content
    return render(request, 'encyclopedia/edit.html', {
        'title': title,
        'content': latest_entry.content if latest_entry else "",
        'original_author': latest_entry.user if latest_entry else None,
        'user': request.user
    })

@login_required
def new_page(request):
    """Create new page (any authenticated user)"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not title or not content:
            messages.error(request, "Title and content are required")
            return render(request, 'encyclopedia/new.html', {
                'title': title,
                'content': content,
                'user': request.user
            })
        
        # Check if page already exists
        existing = Entry.objects.filter(title=title).first()
        if existing is not None:
            messages.info(request, 
                f"Page '{title}' already exists. You can edit the existing page."
            )
            return redirect('edit_page', title=title)
        
        # Create the first version
        Entry.objects.create(
            user=request.user, 
            title=title, 
            content=content
        )
        messages.success(request, f"New page '{title}' created successfully!")
        return redirect('entry', title=title)
    
    return render(request, 'encyclopedia/new.html', {'user': request.user})

def history(request, title):
    """Show edit history of a page"""
    entries = Entry.objects.filter(title=title).order_by('-created_at')
    
    if not entries.exists():
        messages.error(request, f"No history found for '{title}'")
        return redirect('index')
    
    return render(request, 'encyclopedia/history.html', {
        'title': title,
        'entries': entries,
        'user': request.user
    })

def random_page(request):
    """Redirect to random UNIQUE entry"""
    # Get unique titles
    titles = list(Entry.objects.values_list('title', flat=True).distinct())
    
    if not titles:
        return render(request, 'encyclopedia/error.html', {
            'message': "No entries available.",
            'user': request.user
        })
    
    title = random.choice(titles)
    return redirect('entry', title=title)
