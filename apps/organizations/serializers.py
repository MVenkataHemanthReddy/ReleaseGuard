from rest_framework import serializers
from .models import Organisation, Membership


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_email', 'user_name', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrganisationSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'memberships', 'user_role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        user = request.user
        
        # Session authentication - User object
        if hasattr(user, 'is_authenticated') and not hasattr(user, '_project_token'):
            if user.is_authenticated:
                membership = obj.memberships.filter(user=user, is_active=True).first()
                if membership:
                    return membership.role
        
        # ProjectToken authentication - Project object
        elif hasattr(user, 'is_authenticated') and hasattr(user, '_project_token'):
            # For token auth, the project's organisation is the authenticated entity
            # Return a role indicating token access
            if user.organisation.pk == obj.pk:
                return 'token'
        
        return None