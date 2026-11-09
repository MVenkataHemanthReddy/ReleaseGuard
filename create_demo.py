import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from apps.accounts.models import User
from apps.organizations.models import Organisation, Membership
from apps.projects.models import Project, Environment, ProjectToken

# Create admin user if not exists
admin_user, created = User.objects.get_or_create(
    email='admin@example.com',
    defaults={
        'full_name': 'Admin User',
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"Created admin user: {admin_user.email}")
else:
    print(f"Admin user exists: {admin_user.email}")

# Create organization
org, created = Organisation.objects.get_or_create(
    slug='demo-org',
    defaults={'name': 'Demo Organization'}
)
if created:
    print(f"Created organization: {org.name}")

# Create membership
membership, created = Membership.objects.get_or_create(
    user=admin_user,
    organisation=org,
    defaults={'role': 'OWNER'}
)
if created:
    print(f"Created membership: {membership.role}")

# Create project (using 'organisation' not 'organization')
project, created = Project.objects.get_or_create(
    slug='demo-project',
    organisation=org,
    defaults={
        'name': 'Demo Project',
        'description': 'A demo project for ReleaseGuard testing',
    }
)
if created:
    print(f"Created project: {project.name} ({project.id})")

# Create environments (using 'type' field instead of 'slug')
envs = [
    ('Production', 'PRODUCTION'),
    ('Staging', 'STAGING'),
    ('Development', 'DEVELOPMENT'),
]
for name, env_type in envs:
    env, created = Environment.objects.get_or_create(
        project=project,
        name=name,
        defaults={'type': env_type, 'is_default': name == 'Development'}
    )
    if created:
        print(f"Created environment: {env.name} ({env.type})")

# Create project token
token, plain_token = ProjectToken.create_token(
    project=project,
    name='Demo Token',
    description='Demo token for testing'
)
print(f"Created token: {plain_token}")

print(f"\n=== Demo Data Ready ===")
print(f"Project ID: {project.id}")
print(f"Admin login: admin@example.com / admin123")