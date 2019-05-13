from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.index, name='home'),
    path('students/', views.students_page_view, name="students"),
    path('educators/', views.educators_page_view, name="educators"),
    path('leaders/', views.leaders_page_view, name="leaders"),
    path('users/<username>/', views.user_profile, name="user_profile"),
    path('users/<username>/edit/', views.user_edit_view.as_view(), name="user_edit"),
    path('projects/', views.projects_list, name="projects_list"),
    path('projects/<project_uid>/', views.project_view, name="project_view"),
    path('projects/<project_uid>/edit/', views.project_edit_view.as_view(), name="project_edit"),
    path('projects/bypass/<project_uid>/', views.project_view_bypass, name="project_view_bypass"),
    path('user/submit_project', views.submit_project, name='submit_project'),
    path('user/actions/hide_project/<project_uid>/', views.hide_project, name='hide_project'),
    path('user/actions/approve_project/<project_uid>/', views.approve_project, name='approve_project'),
    path('admin/projects_admin', views.projects_admin, name='projects_admin'),
]

handler404 = 'website.views.custom_404'
