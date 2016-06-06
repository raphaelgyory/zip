# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django import forms
from demo_zip.models import ZipApplication


class ZipApplicationForm(forms.ModelForm):

    class Meta:
        model = ZipApplication
        fields = ["name", "description", "file", "is_private"]

    def __init__(self, *args, **kwargs):
        super(ZipApplicationForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'mdl-textfield__input'
        self.fields['description'].widget.attrs['class'] = 'mdl-textfield__input'
        self.fields['file'].widget.attrs['class'] = 'mdl-textfield__input'
        self.fields['is_private'].widget.attrs['class'] = 'mdl-switch__input'

    def add_user(self, user):
        self.user = user
