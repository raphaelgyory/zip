# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


def validate_file_extension(value):
    if not hasattr(value.file, "content_type") or value.file.content_type != 'application/zip':
        raise ValidationError(_('Please upload a zipped package.'))


class ZipApplicationManager(models.Manager):

    def _is_authenticated(self, request, query_dct):
        # if the user is not logged in, we show only public resources
        is_authenticated = request.user.is_authenticated()
        if not is_authenticated:
            query_dct['is_private'] = False
        return is_authenticated

    def _is_staff_or_owner(self, request, query_dct):
        # if the user is not a staff member, he sees only his resources
        is_staff = request.user.is_staff
        if not is_staff:
            query_dct['user'] = request.user
        return is_staff

    def _get_query_dct(self, zip_app_id):
        return {
            "id": zip_app_id,
        }

    def _get_app(self, query_dct):
        # we query the ZipApplication instance or render a forbidden view
        try:
            return ZipApplication.objects.get(**query_dct)
        except Exception:
            raise PermissionDenied

    def get_with_read_right(self, request, zip_app_id):
        """ We check if the user may read the resource. """
        # we prepare the query
        query_dct = self._get_query_dct(zip_app_id)

        # we populate the query dict
        # if the user is auhenticated, he sees only public resources
        is_authenticated = self._is_authenticated(request, query_dct)
        # if he is authenticated, we check if he is the owner or staf
        if is_authenticated:
            self._is_staff_or_owner(request, query_dct)

        return self._get_app(query_dct)

    def get_with_edit_right(self, request, zip_app_id):
        """
        We check if the user owns the resource. The admin may also modify it.
        """
        # we prepare the query
        query_dct = self._get_query_dct(zip_app_id)
        # we populate the query dict
        self._is_staff_or_owner(request, query_dct)
        return self._get_app(query_dct)

    def list_visible(self, request):
        """
        An unauthenticated user sees only public apps.
        The staff sees all of them. A non staff sees the public and the one he owns.
        """
        if request.user.is_authenticated():
            if request.user.is_staff:
                return ZipApplication.objects.all()
            else:
                return ZipApplication.objects.filter(Q(is_private=False) | Q(user=request.user))
        else:
            return ZipApplication.objects.filter(is_private=False)


@python_2_unicode_compatible
class ZipApplication(models.Model):
    """ A zipped application. """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='zips/', validators=[validate_file_extension])
    is_private = models.BooleanField(default=False)
    objects = models.Manager()
    managers = ZipApplicationManager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
