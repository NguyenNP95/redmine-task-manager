from redminelib import Redmine
from django.conf import settings
from .models import RedmineConfiguration


def get_redmine_url():
    """Get Redmine URL from database configuration"""
    return get_config('REDMINE_URL', '')


def get_task_info(task_id, api_key):
    redmine = Redmine(get_redmine_url(), key=api_key)
    task = redmine.issue.get(task_id)

    # Trả về thông tin cần thiết từ task với xử lý các trường hợp không có thuộc tính
    return {
        'tracker': getattr(task.tracker, 'name', None) if hasattr(task, 'tracker') else None,
        'summary': task.subject,
        'status': getattr(task.status, 'name', None) if hasattr(task, 'status') else None,
        'priority': getattr(task.priority, 'name', None) if hasattr(task, 'priority') else None,
        'assignee': getattr(task.assigned_to, 'name', None) if hasattr(task, 'assigned_to') else None,
        'target_version': getattr(task.fixed_version, 'name', None) if hasattr(task, 'fixed_version') else None,
        'parent_task': task.parent.id if hasattr(task, 'parent') else None,
        'start_date': task.start_date if hasattr(task, 'start_date') else None,
        'due_date': task.due_date if hasattr(task, 'due_date') else None,
        'estimate_time': task.estimated_hours if hasattr(task, 'estimated_hours') else None,
        'project_id': task.project.id if hasattr(task, 'project') else None
    }


def create_sub_task_on_redmine(sub_task, api_key, project_id, task_id):
    """
    Tạo sub-task trên Redmine sử dụng Redmine API
    
    Args:
        sub_task (dict): Dictionary chứa thông tin của sub-task cần tạo
        api_key (str): API key của Redmine
        project_id (str): ID của project
        task_id (int): ID của task cha
    
    Returns:
        redminelib.resources.Issue: Đối tượng issue được tạo trên Redmine
    """
    # Khởi tạo kết nối Redmine
    redmine = Redmine(get_redmine_url(), key=api_key)
    
    try:
        # Lấy các ID cần thiết từ Redmine
        trackers = {t.name: t.id for t in redmine.tracker.all()}
        priorities = {p.name: p.id for p in redmine.enumeration.filter(resource='issue_priorities')}
        statuses = {s.name: s.id for s in redmine.issue_status.all()}

        # Chuẩn bị dữ liệu cho sub-task
        issue_data = {
            'project_id': project_id,
            'subject': sub_task['summary'],
            'description': sub_task.get('description', ''),
            'parent_issue_id': task_id,
            'start_date': sub_task.get('start_date'),
            'due_date': sub_task.get('due_date')
        }
        if sub_task.get('estimate_time'):
            issue_data['estimated_hours'] = sub_task.get('estimate_time')
        # Thêm các trường bắt buộc với giá trị mặc định nếu không có
        issue_data['tracker_id'] = trackers.get(sub_task.get('tracker'), trackers.get('Task', list(trackers.values())[0]))
        issue_data['priority_id'] = priorities.get(sub_task.get('priority'), priorities.get('Normal', list(priorities.values())[0]))
        issue_data['status_id'] = statuses.get(sub_task.get('status'), statuses.get('New', list(statuses.values())[0]))

        # Thêm các trường không bắt buộc nếu có
        if sub_task.get('assignee_id'):
            issue_data['assigned_to_id'] = sub_task.get('assignee_id')

        if sub_task.get('target_version'):
            versions = list(redmine.version.filter(project_id=project_id, name=sub_task['target_version']))
            if versions:
                issue_data['fixed_version_id'] = versions[0].id

        # Tạo issue mới trên Redmine
        issue = redmine.issue.create(**issue_data)
        return issue
        
    except Exception as e:
        print(f"Error creating sub-task on Redmine: {str(e)}")
        raise e


def get_config(key, default=None):
    """Get configuration value from database"""
    try:
        config = RedmineConfiguration.objects.get(key=key)
        return config.value
    except RedmineConfiguration.DoesNotExist:
        return default


def get_prefix_task():
    """Get prefix_task configuration from database"""
    prefix_task = {}
    for i in range(7):
        key = f'PREFIX_TASK_{i}'
        value = get_config(key)
        if value:
            prefix_task[i] = value
    return prefix_task or {
        0: '[Study]',
        1: '[Q&A]', 
        2: '[Coding]',
        3: '[UT]',
        4: '[Review]',
        5: '[Fix bug]',
        6: '[Release]'
    }

def get_prefix_tracker():
    """Get prefix_tracker configuration from database"""
    prefix_tracker = {}
    for i in range(7):
        key = f'PREFIX_TRACKER_{i}'
        value = get_config(key)
        if value:
            prefix_tracker[i] = value
    return prefix_tracker or {
        0: 'Task',
        1: 'Q&A',
        2: 'Task', 
        3: 'Task',
        4: 'Task',
        5: 'Task',
        6: 'Task'
    }
