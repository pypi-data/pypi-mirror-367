from django.urls.conf import path

from .admin_site import edc_visit_schedule_app_admin

app_name = "edc_visit_schedule_app"

urlpatterns = [path("admin/", edc_visit_schedule_app_admin.urls)]
