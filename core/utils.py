# -*- coding: utf-8 -*-
from django.db.models import ImageField, FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from PIL import Image
import os
import shutil 
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from django.contrib import admin


def get_ftype(picture):
    if picture.name.endswith(".jpg"):
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'
    elif picture.name.endswith(".png"):
        PIL_TYPE = 'png'
        FILE_EXTENSION = 'png'
    elif picture.name.endswith(".jpeg"):
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'
    elif picture.name.endswith(".gif"):
        PIL_TYPE = 'gif'
        FILE_EXTENSION = 'gif'
    else:
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'

    return PIL_TYPE, FILE_EXTENSION


class ReadOnlyAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        """

        Arguments:
        - `request`:
        - `obj`:
        """
        return not self.__user_is_readonly(request)

    def has_delete_permission(self, request, obj=None):
        """

        Arguments:
        - `request`:
        - `obj`:
        """
        return not self.__user_is_readonly(request)

    def get_actions(self, request):

        actions = super(ReadOnlyAdmin, self).get_actions(request)

        if self.__user_is_readonly(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

    def change_view(self, request, object_id, extra_context=None):

        if self.__user_is_readonly(request):
            self.readonly_fields = self.user_readonly
            self.inlines = self.user_readonly_inlines

        try:
            return super(ReadOnlyAdmin, self).change_view(
                request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(ReadOnlyAdmin, self).change_view(
            request, object_id, extra_context=extra_context)

    def __user_is_readonly(self, request):
        groups = [x.name for x in request.user.groups.all()]
        return "readonly" in groups

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return self.readonly_fields
        return self.readonly_fields


def generate_optim_picture(picture):
    if picture:
        # Copia o genera imagen optimizada
        filename_rel = picture.name 
        filename_abs = os.path.join(settings.MEDIA_ROOT, filename_rel)
        image = Image.open(filename_abs)
        ind1 = filename_rel.rfind('/')
        l = len(filename_rel)
        filename = filename_rel[ind1+1:l]
        resized_dir = os.path.join(settings.MEDIA_ROOT,'images/fotos_productos/optim')  

        image.thumbnail(settings.OPTIMIZED_SIZE, Image.ANTIALIAS)

        format_type, file_extension = get_ftype(picture)

        # Save optimized image version
        temp_thumb = BytesIO()
        image.save(temp_thumb, format_type)
        temp_thumb.seek(0)

        return temp_thumb, filename, file_extension


def generate_thumb_picture(picture):
    if picture:
        # Copia o genera imagen thumbnail
        filename_rel = picture.name 
        filename_abs = os.path.join(settings.MEDIA_ROOT, filename_rel)
        image = Image.open(filename_abs)
        ind1 = filename_rel.rfind('/')
        l = len(filename_rel)
        filename = filename_rel[ind1+1:l]
        thumb_dir = os.path.join(settings.MEDIA_ROOT,'images/fotos_productos/thumb')  

        image.thumbnail(settings.THUMBNAIL_SIZE, Image.ANTIALIAS)

        format_type, file_extension = get_ftype(picture)

        # Save thumbnail image version
        temp_thumb = BytesIO()
        image.save(temp_thumb, format_type)
        temp_thumb.seek(0)

        return temp_thumb, filename, file_extension



class ContentTypeRestrictedImageField(ImageField):
    content_types=settings.PICTURE_TYPES
    max_upload_size=settings.MAX_UPLOAD_PICTURE_SIZE
    '''
    Same as ImageField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
          500KB   -  512000
            2.5MB - 2621440
            5MB - 5242880

    def __init__(self, *args, **kwargs):
        print('kwargs: ', kwargs)
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedImageField, self).__init__(*args, **kwargs)
                10MB - 10485760
    '''

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedImageField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(('Tamaño máximo de archivo permitido: %s. Tamaño actual: %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError('Tipo de archivo no soportado')
        except AttributeError:
            pass

        return data


class ContentTypeRestrictedFileField(FileField):
    content_types=settings.IMAGE_TYPES
    max_upload_size=settings.MAX_UPLOAD_PICTURE_SIZE
    '''
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
          500KB   -  512000
            2.5MB - 2621440
            5MB - 5242880
            1 - 429916160

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)
    '''

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                # PARA EL CASO DE POSTEOS - SOLO SE VALIDA EL TAMAÑO DE LAS FOTOS
                # PERO NO EL DE LOS VIDEOS 
                if file._size > self.max_upload_size and content_type in settings.PICTURE_TYPES:
                    raise forms.ValidationError(('Tamaño máximo de archivo permitido: %s. Tamaño actual: %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError('Tipo de archivo no soportado')
        except AttributeError:
            pass

        return data
