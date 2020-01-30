Pledge to Vote
--------------

This is the Sunrise Movement's Pledge to Vote website. It allows hub organizers (or anyone else with access) to collect information from people who want to pledge to vote at the next election. It also tags each "pledge" with the location where that pledge was entered.

It will eventually push all this data to EveryAction, but that has yet to be implemented.

## Usage
The main portion of the site is protected by a site-wide password. There isn't a user login system, but anyone visiting the site has to enter a password before they can enter any data. When the site is first set up, the active password is `sunrise`. Anyone with admin access (more on that later) can add/remove passwords, and mark certain passwords as active. This allows for different events to use different passwords, even if they're using the site at the same time.

Once logged in, there are a few main views.
* The homepage shows the list of pledges, in descending chronological order.
* Clicking on any of the pledges shown on the homepage brings you to a form where you can edit that pledge.
* Clicking the New Pledge header link brings you to a form where you can enter a new link.
* Clicking the Set Location header link brings you to a form where you can specify your current location (i.e., where you're entering pledges from). You can either choose a pre-existing location, or create a new one. Once you set your location, it will be saved for 24 hours, after which you'll have to re-enter it. This location is associated with each pledge that you submit. (If your location is not set/was set more than 24 hours ago, you'll be redirected to the Set Location page when you try to create a new pledge.)

To create new passwords or disable old passwords, and for more granular editing of the different parts of the system, go to `/admin/`. You have to be a superuser to log in here -- you can create a new superuser with `./manage.py createsuperuser`. I'll talk about that in more detail in the installation/setup instructions below.


## Installation and Setup

I'm going to assume you're using Ubuntu, and are comfortable with the command line here. Feel free to shoot me an email (jesse [at] jesseevers [dot] com) if you need any more guidance. I've included separate instructions for installing locally and on a server.

### Local installation

* Install system-level dependencies: `sudo apt install python3 python3-dev python3-pip python3.7 nodejs npm`
* Install Pipenv: `pip3 install --user pipenv`
* Add Pipenv to the path, by adding this line to `~/.bashrc` (or `~/.zshrc`, if you use `zsh`): `export PATH="$HOME/.local/bin/:$PATH"`
* Clone this repository and change directory into it: `git clone https://github.com/jlevers/sunrise-pledge-to-vote && cd sunrise-pledge-to-vote`
* Copy `.env.example` to `.env`, and fill in the variables in it. You can generate a secret key with [Djecrety](https://djecrety.ir/), and `SITE_URL` should be set to `localhost`.
* From inside the repository directory, install Python packages with `pipenv install`.
* Activate the project's virtual environment with `pipenv shell`.
* Install the packages needed to compile Sass: `./manage.py bulma install`
* Ensure [postgresql](https://www.postgresql.org/) is installed and the `POSTGRES_USERNAME` and `POSTGRES_PASSWORD` match your local database credentials
* Run `psql -c "CREATE DATABASE sunrise_strike_circles"` to initialize the project database
* Run migrations with `./manage.py migrate`
* Create a Django superuser with `./manage.py createsuperuser` (then follow the prompts)
* Start the Django server: `./manage.py runserver`
* Finally, if you're doing active development, start the Sass watch server to make sure Sass gets recompiled when you make changes. Do this in a new terminal, inside the repository: `./manage.py bulma start`

Go to `localhost:8000`, and you should be able to see the site! To access the admin site, go to `localhost:8000/admin`, and enter the credentials you specified when you created a superuser.


### Deploying to a Digital Ocean server

Quick note: these instructions were made well after the site was actually deployed, so some steps might be missing. If you need any help/clarification, shoot me an email at jesse [at] jesseevers [dot] com.

Many of these instructions overlap with the local deploy process.

* Log into [Digital Ocean](https://digitalocean.com). (If you're using the sunrise DO account, ask Andrew Jones for credentials.)
* Create a new Ubuntu 18.04 droplet. The smallest/cheapest option should be fine (1GB RAM, 25GB storage). When you're creating it, there should be an option to add an SSH key -- add yours. This will allow you to SSH into the droplet once it has been created.
* Once you have a droplet, follow the steps in Digital Ocean's [initial server setup guide](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04).
* Install system-level dependencies: `sudo apt install curl python3 python3-dev python3-pip python3.7-dev nginx nodejs npm`
* Install Pipenv: `pip3 install --user pipenv`
* Add Pipenv to the path, by adding this line to `~/.bashrc` (or `~/.zshrc`, if you use `zsh`): `export PATH="$HOME/.local/bin/:$PATH"`
* Do a bare clone this repository and change directory into it: `git clone --bare https://github.com/sunrisemovement/sunrise-strike-circles && cd sunrise-strike-circles.git/`
* Copy `.env.example` to `.env`, and fill in the variables in it. You can generate a secret key with [Djecrety](https://djecrety.ir/), and `SITE_URLS` should be set to a comma-separated list of all domains you might be accessing the project from. When I set it up, the list was `localhost,strikecircle.sunrisemovement.org,<droplet ipv4 address>,<droplet ipv6 address>`, but yours may be different.
* Add the following to the end of your `~/.bashrc`:
```bash
# Adds the settings files to Python's include path.
export PYTHONPATH=$HOME/sunrise-strike-circles/sunrise/settings/:$PYTHONPATH
# Tell Django which settings file to use. The value this is set to MUST be on the $PYTHONPATH.
# See https://docs.djangoproject.com/en/3.0/topics/settings/#envvar-DJANGO_SETTINGS_MODULE for details.
export DJANGO_SETTINGS_MODULE=sunrise.settings.production
```
* In the bare repository you cloned to, create the file `hooks/post-receive` and add the contents of `.githooks/post-receive` to it. You'll have to copy `.githooks/post-receive` from a regular repository, not a bare one -- your local repo will work just fine. Once you've created `hooks/post-receive`, make it executable with `chmod +x hooks/post-receive`.
* In your local repository, add your bare repository as a remote (in this case, I'm naming the remote `deploy`): `git remote add deploy ubuntu@<server-ip>:~/sunrise-strike-circles.git`
* Create a Django superuser with `./manage.py createsuperuser` (then follow the prompts)
* Then, follow Digital Ocean's [guide for deploying a Django app](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04) using Gunicorn, starting where they tell you to "create an exception for port 8000". They use a lot of placeholder names -- don't forget to replace them all with their actual values in this app! For instance, replace `myproject` with `sunrise`, `sammy` with the name of the user you created in the initial setup guide, etc.
* Open up the nginx site configuration that you created in the last step (probably a file like `/etc/nginx/sites-available/sunrise-strike-circles`, or something like that). Add the following, inside the `server` block:
```
...

location /static/ {
    # This redirects all requests to /static/ to /collected_statics/
    rewrite ^/static/(.*)$ /collected_statics/$1 last;
}

location /collected_statics/ {
    # Look in /home/ubuntu/sunrise-strike-circles/ for the collected_statics directory
    root /home/ubuntu/sunrise-strike-circles/;
}
...
```
* When you're done with all that, you should be able to make changes to the production server by pushing from your local `master` like so: `git push deploy`. You're all set!
