# User Leveling System
The user leveling system allows users to create, update, delete and receive information. In this system, each user is assigned a level that determines the level of user access (level zero has the highest access).

## Technologies
* Python 3.10.4
* Django 4.0.4
* djangorestframework 3.13.1
* PyJWT 2.4.0
* pyodbc 4.0.32
* django-pyodbc-azure 2.1.0.0

## make Virtualenv:
* python3 -m venv .env 
* source .env/Scripts/avtivate

## LocalSetup
1) Install All Dependencies  
`pip3 install -r requirements.txt`
2) Database cofiguration 
    * change 'settings.py':
    `https://docs.djangoproject.com/en/4.0/ref/settings/#databases`
    * set:
           ``` DATABASES = {
            "default": {
                "ENGINE": "sql_server.pyodbc",
                "NAME": "user_leveling_db",
                "USER": "sa",
                "PASSWORD": "sa",
                "HOST": "DESKTOP-MTSC260",
                "PORT": "1433",
                "OPTIONS": {
                    "driver": "ODBC Driver 17 for SQL Server",
                    "isolation_level": "READ UNCOMMITTED", 
                    "unicode_results": True
                }
            }
        } ```
3) Change ``INSTALLED_APPS`` 
   ```INSTALLED_APPS = (
        ...,
        'app.apps.AppConfig',
        'rest_framework',
        'drf_yasg',
    )```
    
4) Migrate
`python manage.py makemigrations`
`python manage.py migrate`
5) Run the File   
`python manage.py runserver`

## Run the following link in the browser 
http://127.0.0.1:8000/
## Superuser :
* username:'admin'
* password:'adminadmin'

