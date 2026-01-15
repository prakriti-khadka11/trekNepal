from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import EmergencyAlert

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'emergency_type', 'severity', 'status', 'created_at')
    list_filter = ('severity', 'status')
    search_fields = ('user__username', 'booking__id', 'location', 'emergency_type')
    readonly_fields = ('created_at',)

from django.utils.html import format_html

class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'emergency_type', 'severity_badge', 'status', 'created_at')
    list_filter = ('severity', 'status')

    def severity_badge(self, obj):
        color = {
            'low': 'green',
            'medium': 'orange',
            'critical': 'red'
        }.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.severity
        )
    severity_badge.short_description = 'Severity'
