# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.decorators import method_decorator
from django.views.generic import View
from demo_zip.forms import ZipApplicationForm
from demo_zip.models import ZipApplication
from demo_zip.permissions import PermissionMixin


class ListZipApplications(ListView):

    model = ZipApplication
    template_name = "zip_app_list.html"

    def get_queryset(self):
        """ Returns the ZipApplication instances that the user can see. """
        return ZipApplication.managers.list_visible(self.request)


class UploadZipApplication(SuccessMessageMixin, CreateView):

    initial = dict()
    model = ZipApplication
    form_class = ZipApplicationForm
    template_name = "zip_app_upload.html"
    success_url = reverse_lazy("demo_zip:list")
    success_message = "Congrats, the application has been successfully uploaded!"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UploadZipApplication, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UploadZipApplication, self).form_valid(form)


class UpdateZipApplication(SuccessMessageMixin, PermissionMixin, UpdateView):

    model = ZipApplication
    form_class = ZipApplicationForm
    template_name = "zip_app_upload.html"
    success_url = reverse_lazy("demo_zip:list")
    success_message = "Congrats, the application has been successfully updated!"

    def check_access(self, request):
        return ZipApplication.managers.get_with_edit_right(request, int(self.kwargs['pk']))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateZipApplication, self).dispatch(*args, **kwargs)


class DownloadZipApplication(View):

    def get(self, request, *args, **kwargs):
        """ We check permissions and serve the requested zip package """
        zip_app_id = int(self.kwargs['id'])
        # check permission
        app = ZipApplication.managers.get_with_read_right(request, zip_app_id)
        # get the file
        zipped = open("{0}/{1}".format(settings.MEDIA_ROOT, app.file.name), 'r')
        response = HttpResponse(zipped, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{0}.zip"'.format(app.name)
        return response


class DeleteZipApplication(PermissionMixin, DeleteView):

    model = ZipApplication
    success_url = reverse_lazy("demo_zip:list")

    def check_access(self, request):
        return ZipApplication.managers.get_with_edit_right(request, int(self.kwargs['pk']))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteZipApplication, self).dispatch(*args, **kwargs)
