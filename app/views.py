
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from .models import Project, Milestone, Task
from .forms import RegisterForm, ProjectForm, MilestoneForm, TaskForm


# ================= REGISTER =================

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# ================= LOGIN =================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# ================= LOGOUT =================

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= DASHBOARD =================

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)

    total_projects = projects.count()
    completed_projects = projects.filter(status='Completed').count()
    active_projects = projects.filter(status='In Progress').count()

    total_tasks = Task.objects.filter(
        milestone__project__user=request.user
    ).count()

    completed_tasks = Task.objects.filter(
        milestone__project__user=request.user,
        completed=True
    ).count()

    pending_tasks = total_tasks - completed_tasks

    overdue_projects = projects.filter(
        due_date__lt=timezone.localdate()
    ).exclude(status='Completed').count()

    context = {
        'projects': projects.order_by('-created_at')[:5],
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'active_projects': active_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_projects': overdue_projects,
    }

    return render(request, 'dashboard.html', context)


# ================= PROJECT LIST =================

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)

    search = request.GET.get('search', '')

    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, 'project_list.html', {
        'projects': projects.order_by('-created_at'),
        'search': search,
    })


# ================= ADD PROJECT =================

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()

            messages.success(request, 'Project added successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'project_form.html', {
        'form': form,
        'title': 'Add Project',
    })


# ================= EDIT PROJECT =================

@login_required
def project_update(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_form.html', {
        'form': form,
        'title': 'Edit Project',
    })


# ================= DELETE PROJECT =================

@login_required
def project_delete(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')

    return render(request, 'confirm_delete.html', {
        'object': project,
    })


# ================= PROJECT DETAILS =================

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk,
        user=request.user
    )

    milestones = project.milestones.prefetch_related('tasks').all()

    total_tasks = Task.objects.filter(
        milestone__project=project
    ).count()

    completed_tasks = Task.objects.filter(
        milestone__project=project,
        completed=True
    ).count()

    return render(request, 'project_detail.html', {
        'project': project,
        'milestones': milestones,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress': project.progress(),
    })


# ================= ADD MILESTONE =================

@login_required
def milestone_create(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        user=request.user
    )

    if request.method == 'POST':
        form = MilestoneForm(request.POST)

        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()

            messages.success(request, 'Milestone added successfully!')
            return redirect('project_detail', pk=project.id)
    else:
        form = MilestoneForm()

    return render(request, 'milestone_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Milestone',
    })


# ================= EDIT MILESTONE =================

@login_required
def milestone_update(request, pk):
    milestone = get_object_or_404(
        Milestone,
        pk=pk,
        project__user=request.user
    )

    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)

        if form.is_valid():
            form.save()
            messages.success(request, 'Milestone updated successfully!')
            return redirect('project_detail', pk=milestone.project.id)
    else:
        form = MilestoneForm(instance=milestone)

    return render(request, 'milestone_form.html', {
        'form': form,
        'project': milestone.project,
        'title': 'Edit Milestone',
    })


# ================= DELETE MILESTONE =================

@login_required
def milestone_delete(request, pk):
    milestone = get_object_or_404(
        Milestone,
        pk=pk,
        project__user=request.user
    )

    project_id = milestone.project.id

    if request.method == 'POST':
        milestone.delete()
        messages.success(request, 'Milestone deleted successfully!')

    return redirect('project_detail', pk=project_id)


# ================= ADD TASK =================

@login_required
def task_create(request, milestone_id):
    milestone = get_object_or_404(
        Milestone,
        pk=milestone_id,
        project__user=request.user
    )

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.milestone = milestone
            task.save()

            messages.success(request, 'Task added successfully!')
            return redirect(
                'project_detail',
                pk=milestone.project.id
            )
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {
        'form': form,
        'milestone': milestone,
        'title': 'Add Task',
    })


# ================= EDIT TASK =================

@login_required
def task_update(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        milestone__project__user=request.user
    )

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect(
                'project_detail',
                pk=task.milestone.project.id
            )
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {
        'form': form,
        'milestone': task.milestone,
        'title': 'Edit Task',
    })


# ================= DELETE TASK =================

@login_required
def task_delete(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        milestone__project__user=request.user
    )

    project_id = task.milestone.project.id

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')

    return redirect('project_detail', pk=project_id)


# ================= TASK COMPLETION =================

@login_required
@require_POST
def toggle_task(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        milestone__project__user=request.user
    )

    task.completed = not task.completed
    task.save()

    project = task.milestone.project

    total_tasks = Task.objects.filter(
        milestone__project=project
    ).count()

    completed_tasks = Task.objects.filter(
        milestone__project=project,
        completed=True
    ).count()

    if total_tasks > 0 and completed_tasks == total_tasks:
        project.status = 'Completed'
    elif completed_tasks > 0:
        project.status = 'In Progress'
    else:
        project.status = 'Not Started'

    project.save()

    return redirect('project_detail', pk=project.id)


# ================= WORK REPORT =================

@login_required
def work_report(request):
    projects = Project.objects.filter(
        user=request.user
    ).prefetch_related('milestones__tasks')

    report_data = []

    for project in projects:
        total_tasks = Task.objects.filter(
            milestone__project=project
        ).count()

        completed_tasks = Task.objects.filter(
            milestone__project=project,
            completed=True
        ).count()

        report_data.append({
            'project': project,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress': project.progress(),
        })

    context = {
        'report_data': report_data,
        'total_projects': projects.count(),
        'completed_projects': projects.filter(status='Completed').count(),
        'total_tasks': Task.objects.filter(
            milestone__project__user=request.user
        ).count(),
        'completed_tasks': Task.objects.filter(
            milestone__project__user=request.user,
            completed=True
        ).count(),
    }

    return render(request, 'work_report.html', context)


# ================= EXCEL DOWNLOAD =================

@login_required
def export_excel(request):
    projects = Project.objects.filter(
        user=request.user
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Work Report'

    sheet.append([
        'Project Name',
        'Start Date',
        'Due Date',
        'Status',
        'Total Tasks',
        'Completed Tasks',
        'Progress (%)'
    ])

    for project in projects:
        total_tasks = Task.objects.filter(
            milestone__project=project
        ).count()

        completed_tasks = Task.objects.filter(
            milestone__project=project,
            completed=True
        ).count()

        sheet.append([
            project.title,
            str(project.start_date),
            str(project.due_date),
            project.status,
            total_tasks,
            completed_tasks,
            project.progress(),
        ])

    for cell in sheet[1]:
        cell.font = cell.font.copy(bold=True)

    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or '')) for cell in column
        )
        sheet.column_dimensions[
            column[0].column_letter
        ].width = max_length + 4

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="work_report.xlsx"'
    )

    workbook.save(response)

    return response


# ================= PDF DOWNLOAD =================

@login_required
def export_pdf(request):
    projects = Project.objects.filter(
        user=request.user
    )

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        'attachment; filename="work_report.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(letter)
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph('Freelancer Work Report', styles['Title'])
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f'Generated on: {timezone.localdate()}',
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 20))

    data = [[
        'Project Name',
        'Start Date',
        'Due Date',
        'Status',
        'Total Tasks',
        'Completed Tasks',
        'Progress'
    ]]

    for project in projects:
        total_tasks = Task.objects.filter(
            milestone__project=project
        ).count()

        completed_tasks = Task.objects.filter(
            milestone__project=project,
            completed=True
        ).count()

        data.append([
            project.title,
            str(project.start_date),
            str(project.due_date),
            project.status,
            str(total_tasks),
            str(completed_tasks),
            f'{project.progress()}%',
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3979C9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor('#EAF3FF')
        ]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    document.build(elements)

    return response
