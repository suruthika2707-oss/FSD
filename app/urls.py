
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

    path('projects/<int:project_id>/milestones/add/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:pk>/edit/', views.milestone_update, name='milestone_update'),
    path('milestones/<int:pk>/delete/', views.milestone_delete, name='milestone_delete'),

    path('milestones/<int:milestone_id>/tasks/add/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.toggle_task, name='toggle_task'),

    path('reports/', views.work_report, name='work_report'),
    path('reports/excel/', views.export_excel, name='export_excel'),
    path('reports/pdf/', views.export_pdf, name='export_pdf'),
]
