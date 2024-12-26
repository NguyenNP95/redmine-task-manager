from django.db import migrations

def create_initial_config(apps, schema_editor):
    RedmineConfiguration = apps.get_model('tasks', 'RedmineConfiguration')
    
    # REDMINE_URL
    RedmineConfiguration.objects.create(
        key='REDMINE_URL',
        value='http://localhost:3000',
        description='Redmine server URL'
    )
    
    # Prefix Task
    prefix_tasks = {
        0: '[Study]',
        1: '[Q&A]',
        2: '[Coding]',
        3: '[UT]',
        4: '[Review]',
        5: '[Fix bug]',
        6: '[Release]'
    }
    
    for key, value in prefix_tasks.items():
        RedmineConfiguration.objects.create(
            key=f'PREFIX_TASK_{key}',
            value=value,
            description=f'Prefix for task type {key}'
        )
    
    # Prefix Tracker
    prefix_trackers = {
        0: 'Task',
        1: 'Q&A',
        2: 'Task',
        3: 'Task',
        4: 'Task',
        5: 'Task',
        6: 'Task'
    }
    
    for key, value in prefix_trackers.items():
        RedmineConfiguration.objects.create(
            key=f'PREFIX_TRACKER_{key}',
            value=value,
            description=f'Tracker type for task {key}'
        )

def reverse_initial_config(apps, schema_editor):
    RedmineConfiguration = apps.get_model('tasks', 'RedmineConfiguration')
    RedmineConfiguration.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_config, reverse_initial_config),
    ]