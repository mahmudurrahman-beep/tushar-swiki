# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import re

# Custom manager for entries
class EntryManager(models.Manager):
    def list_entries(self, user=None):
        """Returns list of all entry names for a specific user"""
        if user:
            return list(self.filter(user=user).values_list('title', flat=True))
        return list(self.all().values_list('title', flat=True))
    
    def get_entry(self, title, user=None):
        """Get entry by title for specific user"""
        try:
            if user:
                return self.get(user=user, title=title)
            return self.get(title=title)
        except Entry.DoesNotExist:
            return None
    
    def save_entry(self, title, content, user):
        """Save or update an entry"""
        entry, created = self.update_or_create(
            user=user,
            title=title,
            defaults={'content': content}
        )
        return entry

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
    title = models.CharField(max_length=100, unique=False)  # Remove unique constraint
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = EntryManager()
    
    class Meta:
        unique_together = ['user', 'title']  # Each user can have their own entries
    
    def __str__(self):
        return f"{self.title} (by {self.user.username})"