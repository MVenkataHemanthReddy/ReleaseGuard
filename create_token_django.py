import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from apps.projects.models import Project, ProjectToken

# Get the ShopAPI project
try:
    project = Project.objects.get(slug='shopapi-demo-v3')
    print(f"Found project: {project.name} (ID: {project.id})")
    
    # Create token
    token_obj, token = ProjectToken.create_token(project, 'ShopAPI CI Token')
    print(f"Token created successfully!")
    print(f"Token ID: {token_obj.id}")
    print(f"Token: {token}")
    print(f"Prefix: {token_obj.token_prefix}")
    
except Project.DoesNotExist:
    print("Project not found!")