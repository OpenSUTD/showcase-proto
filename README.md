# OpenSUTD Showcase

## Development

### Test Database Setup (sqlite)

Database will not be pushed to GitHub (will be local on your computer). Use the following script to reset the database.

```bash
./refresh_db.sh
```

### Running the application for development

```bash
# set the GitHub access token for GitHub content integrations
# obtain yours from https://github.com/settings/tokens
# and keep it a secret!!
export GH_ACCESS_TOKEN=XXXXXXX

# make this repo your current directory
cd web-platform-prototype

# to reset the database back to sample values
./refresh_db.sh

# for development without docker
python3 manage.py runserver

# running with docker
# - map port 8000 to port 80
# - mount local folder
TAG=latest-dev
docker run --rm \
 -p 80:8000 \
 --env GH_ACCESS_TOKEN=${GH_ACCESS_TOKEN} \
 -v ${PWD}:/app \
 opensutd/web-platform:${TAG} \
 bash -c " \
  ./refresh_db.sh && \
  python3 manage.py collectstatic --noinput && \
  python3 manage.py runserver 0:8000 "
```

### Getting GitHub login working

1. Create a GitHub Oauth App (https://github.com/settings/developers)
2. Take note of your client ID and secret keys
3. Go to your running Django instance (e.g. http://localhost:8000)
4. Go to http://localhost:8000/admin and log in with default admin credentials (`superadmin` / `asdf1234`)
5. Add a new **Social Application** and fill in the details from step 2
6. Click save and log out from `superadmin`
7. GitHub Login now works

### Unit Tests and CI

```
TODO
```

### Synchronizing your fork to upstream 

You're encouraged to work on your own fork to create contributions. To update your fork with upstream (OpenSUTD main/master repository) changes, please do the following

```bash
# one time setup
git remote add upstream https://github.com/OpenSUTD/web-platform-prototype

# pull upstream changes
git fetch upstream
git merge upstream/master
git push

# errors? check what you need to fix
git status
```

## Acknowledgements

Core project maintainer: [Timothy Liu/@tlkh](https://github.com/tlkh)

(Totally not a web-dev guy, so feedback and criticism is very welcome!)

Original Prototype done by:

* [Timothy Liu/@tlkh](https://github.com/tlkh)
* [Koe Jia-yee/@jiahyphenyee](https://github.com/jiahyphenyee)
* [Ning Sikai/@DoubleCapitals](https://github.com/DoubleCapitals)
* [Bhavy Mital (Grand)/@grand3110](https://github.com/grand3110)




