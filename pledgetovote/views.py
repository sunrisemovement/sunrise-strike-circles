import copy
import datetime

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

from pledgetovote.forms import CreatePledge, SignupForm, StrikeCircleCreateForm, StrikeCircleEditForm
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
    template_name = 'pledgetovote/vis_dashboard.html'

    @staticmethod
    def get_graph_data(sc, agg_fn):
        return {
            'start_week': Pledge.START_WEEK,
            'num_weeks': Pledge.NUM_DATA_COLLECTION_WEEKS,
            'by_week': getattr(sc, agg_fn)()
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
            new_sc = [
                strike_circle['name'],
                strike_circle['goal'],
                sc['current_total'],
                int((sc['current_total'] / strike_circle['goal']) * 100)
            ]
            with_progress.append(new_sc)

        # Sort the top 10 StrikeCircles by progress percentage on the goal
        progress_sorted = sorted(with_progress, key=lambda s: s[3], reverse=True)[:10]

        # Store the current total and percentage completed in a single field
        for sc in progress_sorted:
            sc[2] = f'{sc[2]} ({sc[3]}%)'
            del sc[3]

        return {
            'header_row': ['Strike circle', 'Goal', 'Current total (% completed)'],
            'data': progress_sorted
        }

    def get_context_data(self, **kwargs):
        sc = StrikeCircle.objects.get(user__id=self.request.user.id)

        context = super().get_context_data(**kwargs)
        context.update({
            'pledge_text': Pledge.PLEDGES_TEMPLATE_NAME,
            'one_on_one_text': Pledge.ONE_ON_ONES_TEMPLATE_NAME,

            'pledge_thermometer': {
                'goal': StrikeCircle.objects.aggregate(Sum('pledge_goal'))['pledge_goal__sum'],  # Sum of all pledge goals
                'current': Pledge.objects.all().count(),
            },
            'pledge_graph': Dashboard.get_graph_data(sc, 'num_pledges_by_week'),
            'pledge_leaderboard': Dashboard.get_leaderboard_data('pledge', Pledge.objects.all()),

            'one_on_one_thermometer': {
                'goal': StrikeCircle.objects.aggregate(Sum('one_on_one_goal'))['one_on_one_goal__sum'],  # Sum of all 1-on-1 goals
                'current': Pledge.objects.filter(one_on_one__isnull=False).count(),
            },
            'one_on_one_graph': Dashboard.get_graph_data(sc, 'num_one_on_ones_by_week'),
            'one_on_one_leaderboard': Dashboard.get_leaderboard_data('one_on_one', Pledge.objects.filter(one_on_one__isnull=False))
        })

        return context


class DataEntry(LoginRequiredMixin, TemplateView):
    template_name = 'pledgetovote/data_entry_dashboard.html'

    def post(self, request, *args, **kwargs):
        add_one_on_ones = request.POST.get('add_one_on_ones')
        checked_pledge_form = self._check_post_fields(['first_name', 'last_name', 'email', 'phone', 'yob', 'zipcode', 'date_collected'], request.POST)
        checked_one_on_one_form = self._check_post_fields(['add_one_on_ones'], request.POST)
        if checked_pledge_form:
            cfpf = checked_pledge_form  # Just assigning a shorter variable name for brevity when creating Pledge below
            pledge = Pledge(
                first_name=cfpf['first_name'],
                last_name=cfpf['last_name'],
                email=cfpf['email'],
                phone=cfpf['phone'],
                yob=int(cfpf['yob']),
                zipcode=cfpf['zipcode'],
                date_collected=datetime.datetime.strptime(cfpf['date_collected'], '%Y-%m-%d').date(),
                strike_circle=StrikeCircle.objects.get(user__id=self.request.user.id)
                )
            pledge.save()
        elif checked_one_on_one_form:
            de_stringed = list(map(int, checked_one_on_one_form['add_one_on_ones'].split(',')))
            Pledge.objects.filter(id__in=de_stringed).update(one_on_one=datetime.date.today())

        return HttpResponseRedirect("")

    @staticmethod
    # This method assumes that the headers, fields, and col_classes are in the same order
    def get_listdisplay_data(qs, headers, fields, id=None, col_classes=[], hidden_fields=[]):
        template_data = {'header_row': headers}
        all_data = qs.values(*fields, *hidden_fields)

        if col_classes:
            template_data.update(col_classes=col_classes)

        if id:
            template_data.update(id=id)

        if hidden_fields:
            hidden_data = []
            data = []

            for datum in all_data:
                hidden_row_data = {}
                row_data = []

                for key in datum.keys():
                    # Hidden fields are stored as k/v pairs instead of in arrays, so that
                    # in the template, they can be stored as data attributes with the same
                    # name as the original field
                    if key in hidden_fields:
                        hidden_row_data[key] = datum[key]
                    else:
                        row_data.append(datum[key])

                hidden_data.append(hidden_row_data)
                data.append(row_data)

            template_data.update({
                'hidden_data': hidden_data,
                'data': data
            })
        else:
            template_data['data'] = all_data.values_list(*fields)

        return template_data

    def get_context_data(self, **kwargs):
        sc = StrikeCircle.objects.get(user__id=self.request.user.id)

        week_choices = Pledge.DATA_COLLECTED_DATES
        formatted_choices = [(d.isoformat(), n) for d, n in week_choices]

        context = super().get_context_data(**kwargs)
        context.update({
            'pledge_text': Pledge.PLEDGES_TEMPLATE_NAME,
            'one_on_one_text': Pledge.ONE_ON_ONES_TEMPLATE_NAME,

            'week_choices': formatted_choices,
            'pledge_form': CreatePledge(),
            'pledges': self.get_listdisplay_data(
                sc.pledge_set.all().order_by('-date_created'),
                ['First', 'Last', 'Phone', 'Email', 'Zipcode'],
                ['first_name', 'last_name', 'phone', 'email', 'zipcode'],
                col_classes=['is-2', 'is-2', 'is-3', 'is-3', 'is-2']
            ),
            'no_one_on_one': self.get_listdisplay_data(
                sc.pledge_set.filter(one_on_one__isnull=True).order_by('-date_created'),
                ['First', 'Last'], ['first_name', 'last_name'],
                id='no-one-on-one', hidden_fields=['id']
            ),
            'selected_one_on_ones': self.get_listdisplay_data(
                Pledge.objects.none(),
                ['First', 'Last'], ['first_name', 'last_name'],
                id='selected-one-on-ones', hidden_fields=['id']
            ),
            'completed_one_on_ones': self.get_listdisplay_data(
                sc.pledge_set.filter(one_on_one__isnull=False).order_by('-one_on_one'),
                ['First', 'Last'], ['first_name', 'last_name'],
                id='completed-one-on-ones'
            )
        })

        return context

    # Checks that each of the fields given is actually in the POST data. If it is, the key/value pair field:value is
    # added to the dictionary that's returned. If any field is missing from the POST data, None is returned.
    @staticmethod
    def _check_post_fields(fields, post_data):
        data = {}
        for field in fields:
            gotten = post_data.get(field)
            if not gotten:
                return None
            else:
                data[field] = gotten

        return data


class UpdateStrikeCircle(UpdateView):
    model = StrikeCircle
    form_class = StrikeCircleEditForm
    template_name = 'pledgetovote/sc_edit_form.html'
    success_url = reverse_lazy('pledgetovote:dashboard')

    def get_context_data(self, **kwargs):
        kwargs['form_submit_name'] = "Update"
        return super().get_context_data(**kwargs)

    def get_object(self):
        sc = StrikeCircle.objects.get(id=self.request.user.strikecircle.id)
        return sc


class ProgramGuide(TemplateView):
    template_name = 'pledgetovote/program_guide.html'
