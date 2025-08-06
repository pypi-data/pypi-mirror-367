from django.contrib import admin

from .admin_site import edc_visit_schedule_app_admin
from .models import CrfOne


@admin.register(CrfOne, site=edc_visit_schedule_app_admin)
class CrfOneAdmin(admin.ModelAdmin):
    pass
