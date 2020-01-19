import copy
from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
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
                return HttpResponseRedirect(self.success_url)
            else:
                sc.delete()
                user.delete()
                raise ValidationError("Could not log in user after signing up. Please retry user creation.")

        return self.render_to_response(self.get_context_data(form=user_form))

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Sign up"
        kwargs['sc_form'] = StrikeCircle()
        return super().get_context_data(**kwargs)


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'pledgetovote/dashboard.html'

    @staticmethod
    def get_graph_data(sc, agg_fn):
        start_date = Pledge.FIRST_SC_MEETING_WEEK
        end_date = Pledge.FIRST_SC_MEETING_WEEK + timedelta(weeks=Pledge.NUM_DATA_COLLECTION_WEEKS)
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'by_week': getattr(sc, agg_fn)()
        }

    @staticmethod
    def get_leaderboard_data(goal_type):
        sc_pledge_counts = Pledge.objects.values('strike_circle').annotate(current_total=Count('strike_circle'))
        objectified = sc_pledge_counts.values('current_total', 'strike_circle')

        # Fetch all the StrikeCircles ahead of time so that one doesn't get refetched on every loop iteration
        strike_circles = StrikeCircle.objects.all().values('id', 'name', goal=F(f'{goal_type}_goal'))
        with_progress = []
        for sc in objectified:
            strike_circle = strike_circles.get(id=sc['strike_circle'])
            new_sc = copy.copy(sc)
            new_sc.update({
                'progress': int((sc['current_total'] / strike_circle['goal']) * 100),
                'name': strike_circle['name'],
                'goal': strike_circle['goal']
            })
            with_progress.append(new_sc)

        # Sort the top 10 StrikeCircles by progress percentage on the goal
        progress_sorted = sorted(with_progress, key=lambda s: s['progress'], reverse=True)[:10]

        return progress_sorted

    def get_context_data(self, **kwargs):
        PLEDGES_DISPLAY_NAME = "pledges"
        ONE_ON_ONES_DISPLAY_NAME = "one-on-ones"

        sc = StrikeCircle.objects.get(user__id=self.request.user.id)

        context = super().get_context_data(**kwargs)
        context.update({
            'pledge_text': PLEDGES_DISPLAY_NAME,
            'one_on_one_text': ONE_ON_ONES_DISPLAY_NAME,

            'pledge_thermometer': {
                'goal': StrikeCircle.objects.aggregate(Sum('pledge_goal'))['pledge_goal__sum'],  # Sum of all pledge goals
                'current': Pledge.objects.all().count(),
            },
            'pledge_graph': Dashboard.get_graph_data(sc, 'num_pledges_by_week'),
            'pledge_leaderboard': Dashboard.get_leaderboard_data('pledge'),

            'one_on_one_thermometer': {
                'goal': StrikeCircle.objects.aggregate(Sum('one_on_one_goal'))['one_on_one_goal__sum'],  # Sum of all 1-on-1 goals
                'current': Pledge.objects.filter(one_on_one__isnull=False).count(),
            },
            'one_on_one_graph': Dashboard.get_graph_data(sc, 'num_one_on_ones_by_week'),
            'one_on_one_leaderboard': Dashboard.get_leaderboard_data('one_on_one')
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
