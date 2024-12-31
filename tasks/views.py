# tasks/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TaskLinkForm
from .utils import get_task_info, create_sub_task_on_redmine, get_config, get_prefix_task, get_prefix_tracker
from datetime import datetime
import json
from redminelib import Redmine
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def create_task(request):
    if request.method == 'POST':
        form = TaskLinkForm(request.POST)
        if form.is_valid():
            redmine_api_key = form.cleaned_data['redmine_api_key']
            task_link = form.cleaned_data['task_link']
            task_id = task_link.split('/')[-1]

            try:
                # Lấy REDMINE_URL từ database
                redmine_url = get_config('REDMINE_URL', 'http://localhost:3000')
                
                # Lấy prefix từ database
                prefix_task = get_prefix_task()
                prefix_tracker = get_prefix_tracker()
                
                # Lấy thông tin task từ Redmine với API key từ form
                task_info = get_task_info(task_id, redmine_api_key)
                
                # Lấy các danh sách options từ Redmine
                redmine = Redmine(redmine_url, key=redmine_api_key)
                project_id = task_info['project_id']
                
                # Lấy danh sách trackers, statuses, priorities, users và versions của project
                trackers = list(redmine.tracker.all())
                statuses = list(redmine.issue_status.all())
                priorities = list(redmine.enumeration.filter(resource='issue_priorities'))
                project = redmine.project.get(project_id)
                members = project.memberships
                versions = list(project.versions)

                # Lưu vào session
                request.session['redmine_api_key'] = redmine_api_key
                request.session['redmine_project_id'] = project_id
                request.session['task_id'] = task_id

                # Chuyển đổi các trường date thành string
                if task_info['start_date']:
                    task_info['start_date'] = task_info['start_date'].strftime('%Y-%m-%d')
                if task_info['due_date']:
                    task_info['due_date'] = task_info['due_date'].strftime('%Y-%m-%d')

                # Tính estimate time cho mỗi sub task
                parent_estimate = task_info.get('estimate_time', 0) or 0
                sub_task_estimate = round(parent_estimate / 7, 2) if parent_estimate > 0 else 0

                # Tạo danh sách 7 task con
                sub_tasks = []
                for i in range(len(prefix_task)):
                    sub_task = task_info.copy()
                    sub_task['summary'] = f"{prefix_task[i]}{task_info['summary']}"
                    sub_task['estimate_time'] = sub_task_estimate
                    sub_task['tracker'] = prefix_tracker[i] if i < len(prefix_tracker) else None
                    sub_tasks.append(sub_task)

                # Lưu sub_tasks vào session
                request.session['sub_tasks'] = sub_tasks

                return render(request, 'tasks/create_task.html', {
                    'form': form,
                    'task_info': task_info,
                    'sub_tasks': sub_tasks,
                    'trackers': trackers,
                    'statuses': statuses,
                    'priorities': priorities,
                    'members': members,
                    'versions': versions
                })
            except Exception as e:
                messages.error(request, f'Lỗi khi lấy thông tin task: {str(e)}')
                return render(request, 'tasks/create_task.html', {'form': form})
    else:
        form = TaskLinkForm()

    return render(request, 'tasks/create_task.html', {'form': form})


# tasks/views.py (tiếp theo)
@require_POST
def create_sub_tasks(request):
    try:
        # Lấy thông tin từ session
        sub_tasks = json.loads(request.POST.get('sub_tasks', '[]'))  # Nhận sub_tasks từ form
        api_key = request.session.get('redmine_api_key')
        project_id = request.session.get('redmine_project_id')
        task_id = request.session.get('task_id')
        
        for sub_task in sub_tasks:
            # Chuyển đổi ngày nếu cần
            if sub_task.get('start_date'):
                sub_task['start_date'] = datetime.strptime(sub_task['start_date'], '%Y-%m-%d').date()
            if sub_task.get('due_date'):
                sub_task['due_date'] = datetime.strptime(sub_task['due_date'], '%Y-%m-%d').date()
            
            # Tạo sub-task trên Redmine
            created_task = create_sub_task_on_redmine(sub_task, api_key, project_id, task_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã tạo thành công {len(sub_tasks)} sub-tasks!'
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi tạo sub-tasks: {str(e)}'
        }, status=400)

