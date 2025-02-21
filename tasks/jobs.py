from datetime import datetime
from tasks.utils import get_redmine_statuses, calculate_done_percent
from datetime import datetime
from .models import RedmineAPIKey, JobConfiguration
from .utils import calculate_done_percent, get_redmine_url
from redminelib import Redmine


def update_new_tasks(redmine, user_id):
    """Update tasks from New to In Progress"""
    statuses = get_redmine_statuses(redmine)
    if not statuses['new'] or not statuses['in_progress']:
        raise ValueError("Could not find required status IDs")

    # Lấy tất cả issues có status New
    issues = redmine.issue.filter(
        assigned_to_id=user_id,
        status_id=statuses['new'],
        start_date='><2024-01-01|{}'.format(datetime.now().strftime('%Y-%m-%d'))
    )
    
    for issue in issues:
        # Kiểm tra xem issue có task con không
        children = redmine.issue.filter(parent_id=issue.id)
        if not list(children):  # Nếu không có task con
            redmine.issue.update(
                issue.id,
                status_id=statuses['in_progress']
            )


def update_progress_tasks(redmine, user_id):
    """Update % Done for In Progress tasks"""
    statuses = get_redmine_statuses(redmine)
    if not statuses['in_progress'] or not statuses['closed']:
        raise ValueError("Could not find required status IDs")

    # Lấy tất cả issues có status In Progress
    issues = redmine.issue.filter(
        assigned_to_id=user_id,
        status_id=statuses['in_progress'],
        start_date='><2024-01-01|{}'.format(datetime.now().strftime('%Y-%m-%d'))
    )
    
    today = datetime.now().date()
    
    for issue in issues:
        # Kiểm tra xem issue có task con không
        children = redmine.issue.filter(parent_id=issue.id)
        if not list(children):  # Nếu không có task con
            if not hasattr(issue, 'start_date') or not hasattr(issue, 'due_date'):
                continue
                
            done_percent = calculate_done_percent(
                issue.start_date,
                issue.due_date,
                today
            )
            
            update_data = {'done_ratio': done_percent}
            
            if done_percent >= 100:
                update_data['status_id'] = statuses['closed']
                
            redmine.issue.update(issue.id, **update_data)


def run_daily_update():
    """Main job function"""
    api_keys = RedmineAPIKey.objects.filter(is_active=True)
    redmine_url = get_redmine_url()

    for api_key in api_keys:
        try:
            redmine = Redmine(redmine_url, key=api_key.api_key)
            user = redmine.user.get('current')

            update_new_tasks(redmine, user.id)
            update_progress_tasks(redmine, user.id)

        except Exception as e:
            print(f"Error processing API key {api_key.name}: {str(e)}")

run_daily_update()

