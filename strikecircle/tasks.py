import json

from .env import env
from logging import getLogger
from django.core.serializers import serialize
from strikecircle.models import Pledge, StrikeCircle

from airtable import Airtable
from background_task import background


logger = getLogger(__name__)


API_KEY = env("AIRTABLE_API_KEY")
BASE_KEY = env("AIRTABLE_BASE_KEY")


# TODO: Deploy supervisord in prod to run tasks https://django-background-tasks.readthedocs.io/en/latest/#running-tasks


@background(schedule=10, queue="airtable-export")
def export_strike_circle_to_airtable(strike_circle_id):
	"""
	type: (int) -> Dict[str, Any]
	Export Strike Circle to Airtable so administraters can analyze data.
	"""
	try:
		# Passing raw_record as list because serialization only works for iterable objects: https://code.djangoproject.com/ticket/11244
		strike_circle = StrikeCircle.objects.get(pk=strike_circle_id)
		# TODO: Consider alternatives to serialization for filtering https://stackoverflow.com/a/29088221/4710041
		serialized_record = serialize("json", [strike_circle])
		record = json.loads(serialized_record)[0]
		if record["model"] == "strikecircle.strikecircle":
				table_name = "Strike Circle"
				airtable = Airtable(BASE_KEY, table_name, api_key=API_KEY)
				return airtable.insert(record["fields"])
	except Exception as e:
		logger.error(e)


@background(schedule=10, queue="airtable-export")
def export_pledge_to_airtable(pledge_id):
	"""
	type: (int) -> Dict[str, Any]
	Export Pledge to Airtable so administraters can analyze data.
	"""
	try:
		pledge = Pledge.objects.get(pk=pledge_id)
		# Passing raw_record as list because serialization only works for iterable objects: https://code.djangoproject.com/ticket/11244
		serialized_record = serialize("json", [pledge])
		record = json.loads(serialized_record)[0]
		if record["model"] == "strikecircle.pledge":
			table_name = "Pledge"
			airtable = Airtable(BASE_KEY, table_name, api_key=API_KEY)
			return airtable.insert(record["fields"])
	except Exception as e:
		logger.error(e)	
