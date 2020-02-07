from django.contrib import admin
from strikecircle.models import Pledge, StrikeCircle
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class StrikeCircleResource(resources.ModelResource):

	class Meta:
		model = StrikeCircle


class StrikeCircleAdmin(ImportExportModelAdmin):
	resource_class = StrikeCircleResource


class PledgeResource(resources.ModelResource):

	class Meta:
		model = Pledge

class PledgeAdmin(ImportExportModelAdmin):
	resource_class = PledgeResource


admin.site.register(Pledge, PledgeAdmin)
admin.site.register(StrikeCircle, StrikeCircleAdmin)