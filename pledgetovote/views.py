from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from pledgetovote.forms import SignupForm, StrikeCircleCreateForm
from pledgetovote.models import Pledge, StrikeCircle


class Signup(CreateView):
    form_class = SignupForm
    template_name = 'pledgetovote/base_form.html'
    success_url = reverse_lazy('pledgetovote:dashboard')

    def post(self, request, *args, **kwargs):
        self.object = None
        user_form = self.get_form()
        sc_form = StrikeCircleCreateForm(request.POST)

        if user_form.is_valid() and sc_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            sc = sc_form.save(commit=False)
            sc.user = user
            sc.save()

            authenticated_user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if authenticated_user is not None:
                login(request, authenticated_user)
                return HttpResponseRedirect(self.get_success_url())
            else:
                sc.delete()
                user.delete()
                raise ValidationError("Could not log in user after signing up. Please retry user creation.")

        return self.render_to_response(self.get_context_data(form=user_form))

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Sign up"
        kwargs['sc_form'] = StrikeCircle()
        return super().get_context_data(**kwargs)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verb'] = self.verb

        return context


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.get_object()})
        return kwargs


"""
The view where users can set their Location, either by choosing an existing Location or creating a
new one.
"""
class SetLocation(FormView):
    model = Location
    form_class = LocationForm
    template_name = 'pledgetovote/set_location.html'






"""Displays a list of all Pledges."""
class PledgeList(LoginRequiredMixin, ListView):
    model = Pledge
    context_object_name = 'pledge_list'
    queryset = Pledge.objects.all().order_by('-id')
    paginate_by = 50

"""The view where new Pledges can be created."""
class CreatePledge(CreateView):
    verb = 'Create'
    model = Pledge


"""The view where existing Pledges can be updated."""
class UpdatePledge(UpdateView):
    verb = 'Update'
    model = Pledge
