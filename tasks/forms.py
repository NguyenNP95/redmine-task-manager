# tasks/forms.py
from django import forms


class TaskLinkForm(forms.Form):
    redmine_api_key = forms.CharField(
        label='Redmine API Key',
        required=True,
        widget=forms.TextInput(attrs={'class': 'validate'})
    )
    task_link = forms.URLField(
        label='Redmine Task Link',
        required=True,
        widget=forms.URLInput(attrs={'class': 'validate'})
    )
