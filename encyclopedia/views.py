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
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not username or not password:
            messages.error(request, "Username and password are required")
        elif password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email if email else None
            )
            login(request, user)
            messages.success(request, f"Welcome, {username}! You can now create and edit pages.")
            return redirect('index')
    
    return render(request, 'encyclopedia/register.html')

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
            messages.success(request, f"Welcome back, {username}! You can now edit pages.")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'encyclopedia/login.html')

def logout_view(request):
    """User logout"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('index')

# ============ WIKI VIEWS ============

def index(request):
    """Home page showing ALL entries (public access)"""
    # Show all entries to everyone
    entries = Entry.objects.list_entries()  # No user filter for public viewing
    return render(request, 'encyclopedia/index.html', {
        'entries': entries,
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
    
    return render(request, 'encyclopedia/entry.html', {
        'title': entry_obj.title,
        'content': content_html,
        'entry_user': entry_obj.user,
        'user': request.user
    })

def search(request):
    """Search entries (public access)"""
    query = request.GET.get('q', '').strip()
    entries = Entry.objects.list_entries()  # All entries for searching
    
    if not query:
        return render(request, 'encyclopedia/search.html', {
            'query': query,
            'results': [],
            'user': request.user
        })
    
    # Case-insensitive search
    query_lower = query.lower()
    results = [e for e in entries if query_lower in e.lower()]
    
    return render(request, 'encyclopedia/search.html', {
        'query': query,
        'results': results,
        'user': request.user
    })

@login_required
def new_page(request):
    """Create new page (login required)"""
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
        
        # Check if user already has an entry with this title
        existing = Entry.objects.filter(user=request.user, title=title).first()
        if existing is not None:
            messages.error(request, f"You already have an entry titled '{title}'")
            return render(request, 'encyclopedia/new.html', {
                'title': title,
                'content': content,
                'user': request.user
            })
        
        # Save the entry
        Entry.objects.create(user=request.user, title=title, content=content)
        messages.success(request, f"Page '{title}' created successfully!")
        return redirect('entry', title=title)
    
    return render(request, 'encyclopedia/new.html', {'user': request.user})

@login_required
def edit_page(request, title):
    """Edit existing page (login required - only owner can edit)"""
    # Get the user's specific entry
    entry_obj = Entry.objects.filter(user=request.user, title=title).first()
    
    if entry_obj is None:
        # Check if there's any entry with this title
        any_entry = Entry.objects.filter(title=title).first()
        if any_entry:
            messages.error(request, f"You don't have permission to edit '{title}'. You can create your own version.")
            return redirect('new_page')
        else:
            messages.error(request, f"The page '{title}' doesn't exist.")
            return redirect('new_page')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, "Content cannot be empty")
            return render(request, 'encyclopedia/edit.html', {
                'title': title,
                'content': entry_obj.content,
                'user': request.user
            })
        
        entry_obj.content = content
        entry_obj.save()
        messages.success(request, f"Page '{title}' updated successfully!")
        return redirect('entry', title=title)
    
    return render(request, 'encyclopedia/edit.html', {
        'title': title,
        'content': entry_obj.content,
        'user': request.user
    })

def random_page(request):
    """Redirect to random entry (public access)"""
    entries = Entry.objects.list_entries()  # All entries
    
    if not entries:
        return render(request, 'encyclopedia/error.html', {
            'message': "No entries available.",
            'user': request.user
        })
    
    title = random.choice(entries)
    return redirect('entry', title=title)