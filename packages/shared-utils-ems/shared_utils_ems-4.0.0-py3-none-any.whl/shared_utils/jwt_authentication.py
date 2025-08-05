from rest_framework_simplejwt.authentication import JWTAuthentication
from services.user_management.apps.users.models import AttendeeUser, StaffUser, AdminUser
from rest_framework_simplejwt.exceptions import AuthenticationFailed


ROLE_MODEL_MAP = {
    'attendee': AttendeeUser,
    'admin': AdminUser,
    'staff': StaffUser,
}


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """Override get_user() to support multiple user models."""
        role = validated_token.get('role')
        user_id = validated_token.get('user_id')

        model = ROLE_MODEL_MAP.get(role)
        status = f'is_{role}'

        if not model and not user_id:
            return None

        user = model.objects.filter(id=user_id, **{status: True}).first()

        if user:
            return user
        raise AuthenticationFailed(detail='User not found.')
