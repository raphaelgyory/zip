from django import template
import uuid

register = template.Library()


@register.inclusion_tag('templatetags/zip_app_row.html', takes_context=True)
def zip_app_row(context, zip_application):
    request = context.get('request')
    # we check the user's permission
    may_update = False
    may_delete = False
    if request.user.is_authenticated():
        # we check if the current user has administrative rights or is the owner of the resource
        if request.user.is_staff or request.user == zip_application.user:
            may_update = True
            may_delete = True
    return {'zip_application': zip_application, 'may_update': may_update, 'may_delete': may_delete}


@register.inclusion_tag('templatetags/message_snakbar.html')
def message_snakbar(message):
    return {'message': message}


@register.inclusion_tag('templatetags/input_field.html')
def input_field(input_field):
    # django crispy form is not yet compatible with material design lite
    # furthermore there are some problem in mdl with server side validation:
    # https://github.com/google/material-design-lite/issues/1463
    # we rely on this workaround
    return {'input_field': input_field}


@register.inclusion_tag('templatetags/switch_field.html')
def switch_field(switch_field):
    # see comment in input_field above
    return {'switch_field': switch_field}


@register.inclusion_tag('templatetags/upload_field.html')
def upload_field(upload_field):
    # see comment in input_field above
    return {'upload_field': upload_field}


@register.inclusion_tag('templatetags/password_field.html')
def password_field(upload_field, non_field_errors=None):
    # see comment in input_field above
    return {'password_field': password_field, 'id': uuid.uuid4, 'non_field_errors': non_field_errors}
