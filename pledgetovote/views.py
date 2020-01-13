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


class Dashboard(TemplateView):
    template_name = 'pledgetovote/dashboard.html'

    def get_context_data(self, **kwargs):
        sc = StrikeCircle.objects.get(id=self.request.user.strikecircle.id)
        context = super().get_context_data(**kwargs)
        print(sc.pledge_set.all())
        context.update({
            'pledge_thermometer': {
                'goal': sc.pledge_goal,
                'current': len(sc.pledge_set.all())
            },
            'one_on_one_thermometer': {
                'goal': sc.one_on_one_goal,
                'current': len(sc.pledge_set.filter(one_on_one=True))
            }
        })

        return context


class UpdateStrikeCircle(UpdateView):
    model = StrikeCircle
    fields = ['name', 'pledge_goal', 'one_on_one_goal']
    template_name = 'pledgetovote/base_form.html'
    success_url = reverse_lazy('pledgetovote:dashboard')

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Update"
        return super().get_context_data(**kwargs)

    def get_object(self):
        sc = StrikeCircle.objects.get(id=self.request.user.strikecircle.id)
        print(sc)
        return sc


class PledgeEntry(View):
    pass


class OverallDash(View):
    pass


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
