import json

from logging import getLogger
from django.core.serializers import serialize
from sunrise.settings.env import env
from strikecircle.models import Pledge, StrikeCircle

from airtable import Airtable
from background_task import background


logger = getLogger(__name__)


API_KEY = env("AIRTABLE_API_KEY")
BASE_KEY = env("AIRTABLE_BASE_KEY")

@background(schedule=10, queue="airtable-export")
def export_to_airtable(data_type, obj_id):
    """
    type: (int) -> Dict[str, Any]
    Export Django model data to Airtable so administraters can analyze data.
    """
    try:
        if data_type == 'strikecircle':
            # Passing strike_circle as list because serialization only works for iterable objects: https://code.djangoproject.com/ticket/11244
            strike_circle = StrikeCircle.objects.get(pk=obj_id)
            serialized_record = serialize("json", [strike_circle])
            record = json.loads(serialized_record)[0]
            if record["model"] == "strikecircle.strikecircle":
                table_name = "Strike Circle"
                airtable = Airtable(BASE_KEY, table_name, api_key=API_KEY)
                return airtable.insert(record["fields"])

        elif data_type == 'pledge':
            pledge = Pledge.objects.get(pk=obj_id)
            # Passing pledge as list because serialization only works for iterable objects: https://code.djangoproject.com/ticket/11244
            serialized_record = serialize("json", [pledge])
            record = json.loads(serialized_record)[0]
            if record["model"] == "strikecircle.pledge":
                table_name = "Pledge"
                airtable = Airtable(BASE_KEY, table_name, api_key=API_KEY)
                return airtable.insert(record["fields"])

    except Exception as e:
        logger.error(e)

