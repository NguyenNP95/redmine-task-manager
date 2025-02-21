from django.contrib import admin
from .models import RedmineConfiguration, JobConfiguration, RedmineAPIKey


@admin.register(RedmineConfiguration)
class RedmineConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'value')


@admin.register(JobConfiguration)
class JobConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'value')


@admin.register(RedmineAPIKey)
class RedmineAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_key', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'api_key')
