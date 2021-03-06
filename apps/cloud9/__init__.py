"""
Author: Ross Crawford-d'Heureuse
Description: Default functions to integrate with django-socialregistration
which lacks the appropriate hooks to get AX properties from google.
PLEASE NOTE: need to use the stard0g101 version of django-socialregistration
as per README.markdown
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import Http404
from openid.extensions import ax
from apps.middleware import Http403
#@TODO Turn into Mixin Object

""" Tuple of requested AX urls ((string)<ax_url>, (bool)<is_required>)"""
AX_URLS = getattr(settings, 'SOCIALREGISTRATION_AX_URLS',
    None)


""" ensure that the openid email comes from one of required domains """
def is_valid_domain(domain):
    """ Tuple of allowed_domains """
    ALLOWED_DOMAINS = getattr(settings, 'SOCIALREGISTRATION_ALLOWED_DOMAINS',
        (Site.objects.get_current(),))

    """ method to ensure that the email provided by teopenid provider is allowed """
    if domain in ALLOWED_DOMAINS:
        return True
    else:
        return False


def socialregistration_initial_data(request, user, profile, client):
    args = normalize_openid_keys(client.result.message.getArgs('http://openid.net/srv/ax/1.0'))

    email_parts = parse_email(args['http://openid.net/schema/contact/email'])
    if not is_valid_domain(email_parts['host']):
        raise Http403

    user_data = {
        'username': email_parts['username'],
        'email': args['http://openid.net/schema/contact/email'],
        'first_name': args['http://openid.net/schema/namePerson/first'],
        'last_name': args['http://openid.net/schema/namePerson/last'],
        'profile_picture': '',
    }

    return user_data


""" create an ax object and append the requested AX urls and their is_required status """
def socialregistration_ax_request(auth_request):
    if AX_URLS:
        ax_request = ax.FetchRequest()
        for value in AX_URLS:
            url, is_required = value
            ax_request.add(ax.AttrInfo(url, required=is_required))
        return ax_request
    return None


""" Parse an email address into its basic parts @HACK """
def parse_email(email):
    ob = email.split('@')
    address = dict({
    'username': ob[0],
    'host': ob[1],
    })
    return address


def normalize_openid_keys(openid_args):
    normalized_data = dict({})
    for k,v in openid_args.iteritems():
        token = k.split('.')
        if token[0] == 'type':
           #normalized_data[url]  = v
           key = 'value.%s' % (token[1],)
           normalized_data[v] = openid_args[key]

    return normalized_data
