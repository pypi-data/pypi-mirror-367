from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_visit_schedule_app_admin = EdcAdminSite(
    name="edc_visit_schedule_app_admin", app_label=AppConfig.name
)
