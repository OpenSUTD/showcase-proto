import csv
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opensutd_showcase.settings')
sys.path.append('./')

from github import Github

ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]
gh = Github(ACCESS_TOKEN)

django.setup()

from website.models import *

# create superuser

um = OpenSUTDUserManager()

# TODO create from env variable

um.create_superuser("superadmin", password="asdf1234", display_name="",
                    graduation_year=0, pillar="", personal_links="")

# create users

with open("demo_user_data.csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for row in reader:
        [user_id, display_name, display_picture, graduation_year, pillar] = row
        print(row)

        um.create_user(user_id.lower().strip(), display_name=display_name.strip(),
                       display_picture=display_picture.strip(),
                       graduation_year=graduation_year,
                       pillar=pillar)

def get_stars(project_url):
    """
    Helper function to retrieve GitHub stars
    """
    repo_url = project_url.split("/")
    repo_name = repo_url[-2] + "/" + repo_url[-1]
    repo = gh.get_repo(repo_name)
    return int(repo.stargazers_count)

pm = OpenSUTDProjectManager()

with open("demo_project_data.csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for row in reader:
        [title, caption, category, url,
            status, users, tags, featured_image] = row
        print(row)

        project_uid = title.lower().replace(" ", "-")
        project_uid = category.lower() + "_" + project_uid

        stars = get_stars(url)

        pm.create_project(project_uid=project_uid,
                          title=title,
                          caption=caption,
                          category=category,
                          url=url,
                          stars=stars,
                          featured_image=featured_image)

        for user in users.split(","):
            pm.add_user_to_project(project_uid, user)

        pm.add_tag_to_project(project_uid, tags)

        pm.set_project_status(project_uid, status)

        pm.set_featured_image(project_uid, featured_image)

print("\nAdded Users")
print(User.objects.all())

print("\nAdded Projects")
print(Project.objects.all())
