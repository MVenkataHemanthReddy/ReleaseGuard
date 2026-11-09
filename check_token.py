import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from apps.projects.models import Project, ProjectToken

# Check the token
try:
    token_obj = ProjectToken.objects.get(token_prefix='E2JdUHIZ')
    print(f"Token found: {token_obj.name}")
    print(f"Token ID: {token_obj.id}")
    print(f"Project: {token_obj.project.name} (ID: {token_obj.project.id})")
    print(f"Token prefix: {token_obj.token_prefix}")
    print(f"Is active: {token_obj.is_active}")
    print(f"Project slug: {token_obj.project.slug}")
    
    # Verify the token
    test_token = 'E2JdUHIZPD46CKwtFDcPXhgXkuvs0r94jmDGSOgGsLw'
    is_valid = token_obj.verify_token(test_token)
    print(f"Token verification: {is_valid}")
    
except Exception as e:
    print(f"Error: {e}")