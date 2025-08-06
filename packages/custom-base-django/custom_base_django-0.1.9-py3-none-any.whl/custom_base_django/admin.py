from .models import Choice
from django.contrib import admin

from .models import Choice
from .models.periodict_tasks import PeriodicTasks, RunPeriodicTasks
# Register your models here.
from .models.workflow import Workflow, WorkflowHistory, WorkflowState, BaseStructure
from django_json_widget.widgets import JSONEditorWidget
from django.db import models

admin.site.register([PeriodicTasks, RunPeriodicTasks, Workflow,
                     WorkflowHistory,
                     BaseStructure,
                     ])

class BaseJsonFieldAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, models.JSONField):
            return db_field.formfield(widget=JSONEditorWidget)
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(WorkflowState)
class WorkStateAdmin(BaseJsonFieldAdmin):
    list_display = ('name', 'workflow', 'description')
    search_fields = ['name']
    list_filter = ['name', 'workflow']


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    model = Choice
    extra = 1
    list_display = ['id', 'category', 'title', 'category_title', '__str__']