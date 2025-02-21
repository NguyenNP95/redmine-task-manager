from django.db import migrations


def create_default_configs(apps, schema_editor):
    JobConfiguration = apps.get_model('tasks', 'JobConfiguration')

    JobConfiguration.objects.create(
        key='JOB_RUN_TIME',
        value='16:50',
        description='Daily job execution time'
    )


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0003_jobconfiguration_redmineapikey'),
    ]

    operations = [
        migrations.RunPython(create_default_configs),
    ]