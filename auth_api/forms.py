# -*- encoding: utf-8 -*-
from django import forms
from auth_api.models import User, UserMarca
from django.contrib.auth.models import Group
from mercado_vindu.models import Marca
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from vindu.emails_manager import enviar_reset_psw_mail

class UserAdminForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['field']
        else:
            return []

    def clean_is_staff(self):
        is_staff = self.cleaned_data.get('is_staff')
        if not is_staff:
            raise forms.ValidationError('El usuario debe ser staff')
        return is_staff

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get('is_superuser')
        if not is_superuser:
            raise forms.ValidationError('El usuario debe ser superusuario')
        return is_superuser

    def clean(self):
        is_staff     = self.cleaned_data.get('is_staff')
        is_superuser = self.cleaned_data.get('is_superuser')
        list_groups  = self.cleaned_data.get('groups')
        flag_group_usuario_marca = False
        if is_staff and not is_superuser:
            for group in list_groups:
                if group.name == 'usuario_marca':
                    flag_group_usuario_marca = True

            if not flag_group_usuario_marca:
                raise forms.ValidationError('El Usuario Marca debe pertenecer al grupo usuario_marca')

        return self.cleaned_data


    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserMarcaAdminForm(forms.ModelForm):
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)

    class Meta:
        model = UserMarca
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserMarcaAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True

    def clean_is_staff(self):
        is_staff = self.cleaned_data.get('is_staff')
        if not is_staff:
            raise forms.ValidationError('El usuario debe ser staff')
        return is_staff

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get('is_superuser')
        if is_superuser:
            raise forms.ValidationError('El usuario NO debe ser superusuario')
        return is_superuser

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserMarcaAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CustomPasswordResetForm(PasswordResetForm):

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        UserModel = get_user_model()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % UserModel.get_email_field_name(): email,
            'is_active': True,
        })
        #return (u for u in active_users if u.has_usable_password())
        # Cambio en Vindu: las passwords generadas por Facebook no son usable_passwords
        return (u for u in active_users)

    def save(self, domain_override=None,
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # from django.core.mail import send_mail
        from django.core.mail import EmailMultiAlternatives
        email = self.cleaned_data["email"]
        active_users = self.get_users(email)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            content = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            enviar_reset_psw_mail(request, user, content)



