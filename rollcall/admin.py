from django.contrib import admin
from . import models


@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    actions = ["confirm"]
    readonly_fields = ["student_id", "time"]
    list_display = ["student_id", "time", "confirmed"]

    def confirm(self, request, queryset):
        queryset.update(confirmed=True)
