# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.core.exceptions import PermissionDenied


class PermissionMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not self.check_access(request):
            raise PermissionDenied
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)
