import os
import base64

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import FormView, UpdateView
from django.http import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import *
from .filters import ProjectFilter
from . import models

from github import Github
import markdown2

ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]
gh = Github(ACCESS_TOKEN)

# OpenSUTD Main Pages


def index(request):
    # TODO order by GitHub stars for top projects
    top_projects_list = models.Project.objects.order_by(
        "-stars").filter(status="DISPLAY")[:4]
    recent_projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="DISPLAY")[:9]
    context = {"top_projects_list": top_projects_list,
               "recent_projects_list": recent_projects_list}
    return render(request, "opensutd/home.html", context)


def custom_404(request, exception=None):
    context = {}
    return render(request, "error404.html", context)


def students_page_view(request):
    student_projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="DISPLAY").filter(tags__name__in=["student"])[:9]

    context = {"student_projects_list": student_projects_list}
    return render(request, "opensutd/students.html", context)


def educators_page_view(request):
    educators_projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="DISPLAY").filter(tags__name__in=["education"])[:9]

    context = {"educators_projects_list": educators_projects_list}
    return render(request, "opensutd/educators.html", context)


def leaders_page_view(request):
    policy_projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="DISPLAY").filter(tags__name__in=["policy"])[:9]

    context = {"policy_projects_list": policy_projects_list}
    return render(request, "opensutd/leaders.html", context)

# User Profile and related pages


def user_profile(request, username):
    current_user = models.User.objects.get(username=username)
    current_user.first_login = "False"
    current_user.save()
    user_projects = models.Project.objects.filter(users=current_user)
    context = {"current_user": current_user,
               "user_projects": user_projects}
    return render(request, "user/profile.html", context)


@method_decorator(login_required, name="dispatch")
class user_edit_view(UpdateView):
    # TODO reject if neither admin nor current user

    model = models.User
    form_class = UserProfileForm
    template_name = "user/edit.html"

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(models.User, username=self.kwargs["username"])
        return user

    def get_success_url(self, *args, **kwargs):
        return reverse("website:user_profile", kwargs={'username': self.kwargs["username"]})

# Project List, Showcase and related views


def projects_list(request):
    f = ProjectFilter(
        request.GET, queryset=models.Project.objects.order_by("-published_date").filter(status="DISPLAY"))
    return render(request, "projects/list.html", {"filter": f})


def get_readme_and_stars(current_project_url):
    """
    Helper function to retrieve GitHub README and stars info
    """
    repo_url = current_project_url.split("/")
    repo_name = repo_url[-2] + "/" + repo_url[-1]
    repo = gh.get_repo(repo_name)
    try:
        readme = str(base64.b64decode(
            repo.get_contents("README.md").content))
    except:
        readme = str(base64.b64decode(
            repo.get_contents("readme.md").content))
    readme = readme.replace("\\n", "\n")
    readme = readme.replace("\\'", "'")
    readme = readme[2:-1]  # get rid of b' and '
    readme = markdown2.markdown(
        readme, extras=["fenced-code-blocks", "tables"])

    # fix image paths
    # ignore fully defined paths with http
    readme = readme.replace('src="http', '<|SPECIAL_TOKEN|>')
    readme = readme.replace(
        'src="', 'src="https://raw.githubusercontent.com/' + repo_name + '/master/')
    readme = readme.replace('<|SPECIAL_TOKEN|>', 'src="http')
    readme = readme.replace('<img src="https://github.com/', '<img src="https://raw.githubusercontent.com/')
    readme = readme.replace('/blob/master/', '/master/')

    return readme, str(int(repo.stargazers_count))


def project_view(request, project_uid):
    current_project = models.Project.objects.get(project_uid=project_uid)
    if current_project.is_accepted():
        try:
            readme, stars = get_readme_and_stars(current_project.url)
        except Exception as e:
            readme = "Unable to retrieve README:\n"+str(e)
            stars = "0"

        is_owner = False

        for user in current_project.users.all():
            if user.username == request.user.username:
                is_owner = True
                break

        context = {"current_project": current_project,
                   "is_owner": is_owner,
                   "stars": stars,
                   "readme": readme}

        return render(request, "projects/display.html", context)
    else:
        raise Http404("Project is not yet approved!")


@method_decorator(login_required, name="dispatch")
class project_edit_view(UpdateView):
    # TODO reject if neither admin nor user already attached to project

    model = models.Project
    form_class = ProjectEditForm
    template_name = "projects/edit.html"

    def get_object(self, *args, **kwargs):
        project = get_object_or_404(
            models.Project, project_uid=self.kwargs["project_uid"])
        return project

    def get_success_url(self, *args, **kwargs):
        return reverse("website:project_page", kwargs={'project_uid': self.kwargs["project_uid"]})


@login_required
def project_view_bypass(request, project_uid):
    current_project = models.Project.objects.get(project_uid=project_uid)
    try:
        readme, stars = get_readme_and_stars(current_project.url)
    except Exception as e:
        readme = "Unable to retrieve README:\n"+str(e)
        stars = "0"

    context = {"current_project": current_project,
               "stars": stars,
               "readme": readme}

    return render(request, "projects/display.html", context)


@login_required
def submit_project(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = SubmissionForm(request.POST)
        # check whether form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            data = form.cleaned_data
            pm = models.OpenSUTDProjectManager()
            project_uid = data["project_name"].upper().replace(" ", "_")

            pm.create_project(project_uid=project_uid,
                              title=data["project_name"],
                              caption=data["caption"],
                              category=data["category"],
                              url=data["github_url"],
                              featured_image=data["featured_image"])

            pm.add_user_to_project(project_uid, request.user.username)

            # redirect to a new URL:
            return HttpResponseRedirect("/user/"+request.user.username+"/")

    # if a GET (or any other method) we"ll create a blank form
    else:
        form = SubmissionForm()

    return render(request, "projects/submit.html", {"form": form})

# project admin view


@login_required
def projects_admin(request):
    projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="PENDING")[:50]
    hidden_projects_list = models.Project.objects.order_by(
        "-published_date").filter(status="HIDDEN")[:50]
    context = {"projects_list": projects_list,
               "hidden_projects_list": hidden_projects_list, }
    return render(request, "projects/admin.html", context)


@login_required
def approve_project(request, project_uid):
    project = models.Project.objects.get(project_uid=project_uid)
    project.status = "DISPLAY"
    project.save()
    return HttpResponseRedirect("/admin/approval")


@login_required
def hide_project(request, project_uid):
    project = models.Project.objects.get(project_uid=project_uid)
    project.status = "HIDDEN"
    project.save()
    return HttpResponseRedirect("/admin/approval")
