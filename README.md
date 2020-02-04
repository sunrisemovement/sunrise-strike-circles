Strike Circles
--------------

This is the Sunrise Movement's Strike Circles website. It allows Strike Circle organizers (or anyone else with access) to input, edit, and visualize data about people who've pledged to vote both for their own hub, and for all hubs across the entire movement.

## Usage

Each user must have an associated Strike Circle. This is automatically dealt with when a new account is created via the Signup page, because the user signup and Strike Circle creation forms have been combined into a single form.

Once they have an account, a Strike Circle can set their goals for the number of pledges that they intend to get, and the number of one-on-ones they plan on doing. The main data dashboard page shows them their progress towards those goals, as well as the cumulative progress of all Strike Circles in the movement towards their total goal. There's also a leaderboard showing the top 5 Strike Circles, as judged by how close they are to reaching their goals.

There's also a data input page, where Strike Circles can input new pledges, edit existing pledges, and mark pledges as having had one-on-ones.

The last major page, the Program Guide page, just contains an embedded PDF of the Strike Circle organizing document.

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

#### Troubleshooting

##### `An error occurred while installing psycopg2==2.8.4`
Possible cuase: `fatal error: Python.h: No such file or directory`. If so, install the dev version of python: `sudo apt-get install python3.7-dev`


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
