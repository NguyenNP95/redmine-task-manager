import os
import django

# Cấu hình Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redmine_task_manager.settings')
django.setup()

# Import sau khi đã cấu hình Django
from tasks.jobs import run_daily_update

if __name__ == '__main__':
    try:
        print("Starting daily update job...")
        run_daily_update()
        print("Daily update completed successfully!")
    except Exception as e:
        print(f"Error occurred: {str(e)}") 