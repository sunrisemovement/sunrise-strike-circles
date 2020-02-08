import copy
import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from strikecircle.forms import CreatePledgeFormSet, PledgeFormSet, SignupForm, StrikeCircleCreateForm, StrikeCircleEditForm
from strikecircle.models import Pledge, StrikeCircle


class Signup(CreateView):
    form_class = SignupForm
    template_name = 'strikecircle/base_form.html'
    success_url = reverse_lazy('strikecircle:dashboard')

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

        return render(request, self.template_name, self.get_context_data(form=user_form))

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Sign up"
        kwargs['sc_form'] = StrikeCircle()
        return super().get_context_data(**kwargs)


class SunriseLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class ProgressDashboard(SunriseLoginRequiredMixin, TemplateView):
    template_name = 'strikecircle/progress_dashboard.html'

    @staticmethod
    def get_graph_data(sc, goal_type):
        return {
            'start_week': Pledge.START_WEEK,
            'num_weeks': Pledge.NUM_DATA_COLLECTION_WEEKS,
            'goal': getattr(sc, f'{goal_type}_goal'),
            # Assumes that for each goal, there's a method named num_<goal-related-field>s_by_week that aggregates (by week) the
            # number of Pledges belonging to the given StrikeCircle with that goal field completed
            'by_week': getattr(sc, f'num_{goal_type}s_by_week')()
        }

    @staticmethod
    def get_leaderboard_data(goal_type, qs):
        sc_pledge_counts = qs.values('strike_circle').annotate(current_total=Count('strike_circle'))
        objectified = sc_pledge_counts.values('current_total', 'strike_circle')

        # Fetch all the StrikeCircles ahead of time so that one doesn't get refetched on every loop iteration
        strike_circles = StrikeCircle.objects.all().values('id', 'name', goal=F(f'{goal_type}_goal'))
        with_progress = []
        for sc in objectified:
            strike_circle = strike_circles.get(id=sc['strike_circle'])

            if strike_circle['goal'] == 0:
                continue

            new_sc = [
                strike_circle['name'],
                strike_circle['goal'],
                sc['current_total'],
                int((sc['current_total'] / strike_circle['goal']) * 100)
            ]
            with_progress.append(new_sc)

        # Sort the top 10 StrikeCircles by progress percentage on the goal
        progress_sorted = sorted(with_progress, key=lambda s: s[3], reverse=True)[:5]

        # Store the current total and percentage completed in a single field
        for sc in progress_sorted:
            sc[2] = f'{sc[2]} ({sc[3]}%)'
            del sc[3]

        return {
            'header_row': ['Strike circle', 'Goal', 'Current total (% completed)'],
            'col_classes': ['is-6', 'is-2', 'is-4'],
            'data': progress_sorted
        }

    def get_context_data(self, **kwargs):
        sc = StrikeCircle.objects.get(user__id=self.request.user.id)

        context = super().get_context_data(**kwargs)

        pledge_graph = ProgressDashboard.get_graph_data(sc, 'pledge')
        pledge_graph['goal_type'] = 'pledges'

        # Don't include Week 2 in the one-on-ones graph
        one_on_one_graph = ProgressDashboard.get_graph_data(sc, 'one_on_one')
        one_on_one_graph['start_week'] += 1
        one_on_one_graph['num_weeks'] -= 1
        one_on_one_graph['goal_type'] = 'one-on-ones'

        context.update({
            'pledge_text': Pledge.PLEDGES_TEMPLATE_NAME,
            'one_on_one_text': Pledge.ONE_ON_ONES_TEMPLATE_NAME,

            'sc': sc,
            'pledge_graph_data': pledge_graph,
            'one_on_one_graph_data': one_on_one_graph,

            'pledge_progress_bar_data': {
                'goal': StrikeCircle.objects.aggregate(Sum('pledge_goal'))['pledge_goal__sum'],  # Sum of all pledge goals
                'current': Pledge.objects.all().count()
            },
            'pledge_leaderboard_data': ProgressDashboard.get_leaderboard_data('pledge', Pledge.objects.all()),

            'one_on_one_progress_bar_data': {
                'goal': StrikeCircle.objects.aggregate(Sum('one_on_one_goal'))['one_on_one_goal__sum'],  # Sum of all 1-on-1 goals
                'current': Pledge.objects.filter(one_on_one__isnull=False).count()
            },
            'one_on_one_leaderboard_data': ProgressDashboard.get_leaderboard_data('one_on_one', Pledge.objects.filter(one_on_one__isnull=False))
        })

        return context


class DataInput(SunriseLoginRequiredMixin, TemplateView):
    model = Pledge
    template_name = 'strikecircle/data_input_dashboard.html'
    context_object_name = 'pledges'

    def post(self, request, *args, **kwargs):
        formset_type = request.POST['form_type']
        FormSetClass = PledgeFormSet if formset_type == 'edit' else CreatePledgeFormSet
        formset = FormSetClass(request.POST)

        if formset.is_valid():
            if formset_type == 'edit':
                formset.save()
            else:
                sc = StrikeCircle.objects.get(user__id=request.user.id)
                for form in formset:
                    if form.cleaned_data != {}:
                        pledge = form.save(commit=False)
                        pledge.strike_circle = sc
                        pledge.save()

        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def get_queryset(self):
        sc = StrikeCircle.objects.get(user__id=self.request.user.id)
        return Pledge.objects.filter(strike_circle=sc).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fields = ['first_name', 'last_name', 'email', 'phone', 'zipcode', 'yob', 'date_collected', 'one_on_one']
        hidden_fields = ['id']
        paginator = Paginator(self.get_queryset(), 20)
        page_num = self.request.GET.get('page')
        page_obj = paginator.get_page(page_num)
        qs = page_obj.object_list

        context.update({
	    'page_obj': page_obj,
	    'ellipsis_start': page_obj.number > 3,
	    'ellipsis_end': page_obj.number < paginator.num_pages - 2,
            'table': {
                'data': qs.values(*fields),
                'hidden_data': qs.values(*hidden_fields),
                'header_row': ['First name', 'Last name', 'Email address', 'Phone #', 'Zipcode', 'YOB', 'Week pledged', 'One-on-one completed?'],
                'fields': fields,
                'col_classes': ['is-1', 'is-1', 'is-3', 'is-1', 'is-1', 'is-1', 'is-2', 'is-2']
            },
            'add_pledges_formset': kwargs.get('add_pledges_formset', CreatePledgeFormSet(queryset=Pledge.objects.none())),
            'edit_pledges_formset': kwargs.get('edit_pledges_formset', PledgeFormSet(queryset=qs)),
            'misc_data': {
                'week_map': Pledge.DATA_COLLECTED_DATES
            }
        })

        return context


class UpdateStrikeCircle(SunriseLoginRequiredMixin, UpdateView):
    model = StrikeCircle
    form_class = StrikeCircleEditForm
    template_name = 'strikecircle/sc_edit_form.html'
    success_url = reverse_lazy('strikecircle:dashboard')

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Update"
        return super().get_context_data(**kwargs)

    def get_object(self):
        sc = StrikeCircle.objects.get(id=self.request.user.strikecircle.id)
        return sc


class ProgramGuide(SunriseLoginRequiredMixin, TemplateView):
    template_name = 'strikecircle/program_guide.html'
