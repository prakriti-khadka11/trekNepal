from django.contrib import admin
from django.utils.html import format_html
from .models import EmergencyAlert

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'emergency_type', 'severity_badge', 'status', 'created_at')
    list_filter = ('severity', 'status', 'emergency_type', 'created_at')
    search_fields = ('user__username', 'booking__id', 'location', 'emergency_type')
    readonly_fields = ('created_at',)

    def severity_badge(self, obj):
        color = {
            'low': 'green',
            'medium': 'orange',
            'critical': 'red'
        }.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
