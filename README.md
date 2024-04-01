# Planetarium

API service for managing planetarium written on DRF.

# Installing using GitHub
Install PostgreSQL and create db

```shell
git clone git@github.com:NataliiaKorzh/Planetarium-API.git

python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver

```
# Run with Docker

Docker should be installed
```shell
docker-compose build
docker-compose up
```
# Getting access
create user via /api/user/register/

get access token via /api/user/token/

# Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located on /api/doc/swagger/
- Managing reservations and tickets
- Creating show themes
- Creating planetarium domes
- Creating astronomy shows
- Creating show seasons
- Filtering astronomy shows by title

![DB structure](DB-structure.png)
