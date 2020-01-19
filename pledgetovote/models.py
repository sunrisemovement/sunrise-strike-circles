from datetime import date, timedelta

from django.core.validators import EmailValidator
from django.contrib.auth.models import User
from django.db import models
from localflavor.us.models import USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField


class StrikeCircle(models.Model):
    name = models.CharField(max_length=100)
    pledge_goal = models.IntegerField(default=0)
    one_on_one_goal = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def num_pledges_by_week(self):
        by_week = []
        for _, week_start_date in enumerate(Pledge.DATA_COLLECTED_DATES):
            week_num = week_start_date[0].isocalendar()[1]
            num_in_week = self.pledge_set.filter(date_collected__week__lte=week_num).count()
            by_week.append(num_in_week)

        return by_week

    def num_one_on_ones_by_week(self):
        by_week = []
        for _, week_start_date in enumerate(Pledge.DATA_COLLECTED_DATES):
            week_num = week_start_date[0].isocalendar()[1]
            num_in_week = self.pledge_set.filter(one_on_one__isnull=False, one_on_one__week__lte=week_num).count()
            by_week.append(num_in_week)

        return by_week

    def __str__(self):
        return f"<StrikeCircle {self.name}>"


class Pledge(models.Model):
    YEAR_CHOICES = [(i, i) for i in range(date.today().year, 1900, -1)]

    # Strike Circles meet for the first time the week of 2/10/2020, and start canvassing the following week
    DAYS_PER_WEEK = 7
    START_WEEK = 2
    """
    TODO: Figure out why replacing `date(2020, 2, 10)` with FIRST_SC_MEETING_WEEK in DATA_COLLECTED_DATES results in
    "NameError: name 'FIRST_SC_MEETING_WEEK' is not defined"
    """
    FIRST_SC_MEETING_WEEK = date(2020, 2, 10)
    NUM_DATA_COLLECTION_WEEKS = 5
    DATA_COLLECTED_DATES = [(date(2020, 2, 10) + timedelta(weeks=(i - 1)), f'Week {i}')
                                for i in range(START_WEEK, START_WEEK + NUM_DATA_COLLECTION_WEEKS)]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, validators=[EmailValidator], unique=True)
    phone = PhoneNumberField()
    zipcode = USZipCodeField(max_length=5)
    yob = models.IntegerField(choices=YEAR_CHOICES)
    one_on_one = models.DateField(blank=True, null=True)
    date_collected = models.DateField(choices=DATA_COLLECTED_DATES)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    strike_circle = models.ForeignKey(StrikeCircle, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email} :: last modified {self.date_modified})"
