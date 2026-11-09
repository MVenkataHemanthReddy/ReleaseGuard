"""
Admin configuration for projects app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.projects.models import Project, Environment, ProjectToken


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation', 'slug', 'is_active', 'created_at', 'deleted_at')
    list_filter = ('is_active', 'organisation__is_active', 'created_at', 'deleted_at')
    search_fields = ('name', 'slug', 'description', 'organisation__name')
    ordering = ('organisation__name', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    raw_id_fields = ('organisation',)
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('organisation', 'name', 'slug', 'description', 'repository_url', 'is_active')}),
        (_('Metadata'), {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'type', 'is_default', 'is_active', 'created_at', 'deleted_at')
    list_filter = ('type', 'is_default', 'is_active', 'project__organisation', 'created_at', 'deleted_at')
    search_fields = ('name', 'project__name', 'description')
    ordering = ('project__name', 'type', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    raw_id_fields = ('project',)

    fieldsets = (
        (None, {'fields': ('project', 'name', 'type', 'description', 'base_url', 'is_active', 'is_default')}),
        (_('Metadata'), {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )


@admin.register(ProjectToken)
class ProjectTokenAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'token_prefix', 'is_active', 'expires_at', 'last_used_at', 'created_at', 'deleted_at')
    list_filter = ('is_active', 'project__organisation', 'created_at', 'expires_at', 'deleted_at')
    search_fields = ('name', 'project__name', 'token_prefix', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'token_hash', 'token_prefix', 'created_at', 'updated_at', 'deleted_at', 'last_used_at')
    raw_id_fields = ('project',)

    fieldsets = (
        (None, {'fields': ('project', 'name', 'description', 'is_active', 'expires_at')}),
        (_('Token Info (read-only)'), {'fields': ('token_prefix', 'token_hash', 'last_used_at')}),
        (_('Metadata'), {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )

    def has_add_permission(self, request):
        # Tokens should be created via API/management command, not admin
        return False

    def has_change_permission(self, request, obj=None):
        # Allow deactivation but not hash/prefix changes
        return True