from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token


    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            # here changing model.objects.select_related('user').get(key=key) to 
            # model.objects.select_related('user').get(token=key)
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo o inexistente')

        return (token.user, token)
