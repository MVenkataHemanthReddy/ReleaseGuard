import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from apps.projects.models import Project

projects = list(Project.objects.values('id', 'name', 'slug'))
print("Projects:", projects)