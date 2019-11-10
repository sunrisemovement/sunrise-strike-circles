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

I'm going to assume some familiarity with Linux and the command line here. Feel free to shoot me an email (jesse27999 [at] gmail [dot] com) if you need any more guidance.

Step by step:

* Install system dependencies (Ubuntu): `sudo apt-get install python3 python3-dev python3-pip nodejs npm`
* Install package dependencies: `pip3 install --user pipenv`
* Clone this repository: `git clone https://github.com/jlevers/sunrise-pledge-to-vote`
* Then, from inside the repository directory, install Python packages with `pipenv`: `pipenv install`
* Install the packages needed to compile Sass: `./manage.py bulma install`
* Run migrations with `./manage.py migrate`
* Create a Django superuser with `./manage.py createsuperuser` (then follow the prompts)
* Start the Django server: `./manage.py runserver`
* Finally, if you're doing active development, start the Sass watch server to make sure Sass gets recompiled when you make changes. Do this in a new terminal, inside the repository: `./manage.py bulma start`

Go to `localhost:8000`, and you should be able to see the site! To access the admin, go to `localhost:8000/admin`, and enter the credentials you specified when you created a superuser.
