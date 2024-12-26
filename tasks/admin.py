from django.contrib import admin
from .models import RedmineConfiguration

@admin.register(RedmineConfiguration)
class RedmineConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'value')
