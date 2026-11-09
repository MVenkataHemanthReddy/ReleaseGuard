"""
Admin configuration for organizations app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import Organisation, Membership


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at', 'deleted_at')
    list_filter = ('is_active', 'created_at', 'deleted_at')
    search_fields = ('name', 'slug', 'description')
    ordering = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'is_active')}),
        (_('Metadata'), {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation', 'role', 'is_active', 'created_at', 'deleted_at')
    list_filter = ('role', 'is_active', 'organisation__is_active', 'created_at', 'deleted_at')
    search_fields = ('user__email', 'user__full_name', 'organisation__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    raw_id_fields = ('user', 'organisation')

    fieldsets = (
        (None, {'fields': ('user', 'organisation', 'role', 'is_active')}),
        (_('Metadata'), {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )