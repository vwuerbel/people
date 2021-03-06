# encoding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.base import View
from django.http import Http404
from django.contrib.auth.models import User

from socialregistration.views import Setup

from forms import AccountEditForm
from models import AdcloudInfo
from apps.util import user_is_self_or_admin, anonymous_required



def default(request):
    """ 
    Default view, applies the spcified pre-login routing rules
    basically unless logged in everythign routes to /login
    and once logged in the people list is the default view 
    (this may change as the system expands in the future)
    """
    is_loggedin = request.user.is_authenticated()

    if not is_loggedin:
      object_list = User.objects.select_related('profile').filter(profile__is_public=True,is_active=True,is_superuser=False).order_by('first_name', 'last_name')
    elif is_loggedin:
      object_list = User.objects.select_related('profile').filter(is_active=True,is_superuser=False).order_by('first_name', 'last_name')

    return render_to_response('cloud9/home.html', {
        'object_list': object_list,
        'is_loggedin': is_loggedin,
    },context_instance=RequestContext(request))

    # else:
    #     return render_to_response('cloud9/base.html', {'request':request}, context_instance=RequestContext(request))

@anonymous_required
def login(request):
    """
    Basically a direct to template renderer but the requirement of the request object
    is met here (request was not provided by default @TODO must check docs)
    """
    return render_to_response('cloud9/login.html', {'request':request}, context_instance=RequestContext(request))


class EmployeeEdit(Setup):
    """
    Inherited form the base socialregistration.Setup form and catering to our specific edit flow
    """
    template_name = 'socialregistration/edit.html'

    def get_form(self):
        """
        Override the default to use the EmployeeEdit form
        """
        return self.import_attribute('apps.cloud9.forms.AccountEditForm')

    def get_initial_data(self, request, user, profile, client):
        """
        Overridden get data method which is used to populate the form
        """
        skills = []
        for skill in user.profile.skills.all():
            skills.append(skill.name)
        skills = ','.join(skills)
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.profile.title,
            'bio': user.profile.bio,
            'department': user.profile.department,
            'team': user.profile.team,
            'workplace': user.profile.workplace,
            'room_number': user.profile.room_number,
            'contact_phone': user.profile.contact_phone,
            'profile_picture': user.profile.profile_picture,
            'skype': user.profile.skype,
            'twitter': user.profile.twitter,
            'is_public': user.profile.is_public,
            'skills': skills,
        }
        return data

    def get(self, request, slug):
        """
        Overriden Get process, allows for the User.profile object
        @TODO is probably redundant now thanks to django-annoying.AutoOneToOneField
        field useage
        """
        user = get_object_or_404(User, username=slug)
        allowed_access = user_is_self_or_admin( request, user )
        if not allowed_access == True:
            return allowed_access

        try:
            profile = user.profile
        except AdcloudInfo.DoesNotExist:
            profile = AdcloudInfo.objects.get_or_create(user=user)

        client = None

        form = self.get_form()(initial=self.get_initial_data(request, user, profile, client))

        return self.render_to_response(dict(form=form, object=user))

    def post(self, request, slug):
        """
        Save the user and profile, login and send the right signals.
        """
        from socialregistration.contrib.openid.models import OpenIDProfile

        user = get_object_or_404(User, username=slug)
        allowed_access = user_is_self_or_admin( request, user )
        if not allowed_access == True:
            return allowed_access

        try:
            profile = OpenIDProfile.objects.get(user=user)
        except OpenIDProfile.DoesNotExist:
            profile = OpenIDProfile.objects.get_or_create(user=user)
        client = None

        form = self.get_form()(request.POST, request.FILES, initial={'profile_picture': user.profile.profile_picture})

        if not form.is_valid():
            return self.render_to_response(dict(form=self.get_form()(request.POST, initial={'profile_picture': user.profile.profile_picture})))

        user, profile = form.save(request, user, profile, client)

        profile.authenticate()

        return redirect(reverse('cloud9:employee_detail', kwargs={'slug':user.username}))


class ContactPhoneQRCode(DetailView):
    model = AdcloudInfo

    def render_to_response(self, context, **response_kwargs):
        image_data = context['object'].phone_qr()
        response = HttpResponse(mimetype="image/png")
        image_data.save(response, "PNG")
        return response