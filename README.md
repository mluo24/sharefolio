# Sharefolio

This project was originally made as a passion project/to test out Django, and it was partially extended for my high school senior project but was canceled due to the COVID-19 pandemic.

---

## Details

Make your creative portfolio and share it with others and receive feedback, all in one community!

As of right now, it is an app for sharing original works of (chaptered) fiction (think Wattpad/Archive of Our Own). In the future, this project hopes to see more forms of mediums being added in, most notably photos/artworks, as well as more fleshed out community/constructive feedback features.

## Features

Currently, this app supports the following:

- User signup/login/profiles
- Posting new stories, adding chapters to stories
- Draft/published and ongoing/completed system
- Comments on stories
- Categories and tags

Some planned features include:

- Follower system
- Better liked system
- Images (and more!) as an art medium
- Filter by tags
- Better look

## Installation (to try it out)

Clone this repository. Make sure you have a Python version of at least 3.8 and PostgreSQL downloaded and set up with a database and proper user permissions.

Create a virtual environment (named `venv`) and install the requirements.txt. If you get an error from Pillow about a dependency, install it first.

### .env file

Create a `.env` file in the root directory with the following variables with their respective correct values:

```
DEBUG=True
SECRET_KEY=<SECRET KEY>
DATABASE_NAME=<DATABASE NAME>
DATABASE_USER=<DATABASE USERNAME>
DATABASE_PASSWORD=<DATABASE PASSWORD>
DATABASE_HOST=<DATABASE HOST>
DATABASE_PORT=<DATABASE PORT>
```

You can generate a secret key with this command: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

### Migrations and Next Steps

Your database should be properly set up as of this point. To run migrations, run the command `python manage.py migrate`.

To create a superuser (a user with all the admin permissions at http://localhost:8000/admin), run `python manage.py createsuperuser`. You can also use this account to log in for the rest of the app.

Run the server with `python manage.py runserver`. The API (or the actual site) should now be running properly locally (http://localhost:8000 by default)!
