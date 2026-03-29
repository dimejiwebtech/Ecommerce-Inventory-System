from django.contrib.auth.backends import ModelBackend

from accounts.models import CustomUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get('email')
        try:
            user = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            return None
        except CustomUser.MultipleObjectsReturned:
            user = CustomUser.objects.filter(email__iexact=email).order_by('id').first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
