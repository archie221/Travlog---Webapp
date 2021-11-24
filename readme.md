Instructions to install django with mysql:
1. python3 -m venv my_env
2. sudo apt install python3-pip python3-venv
3. source my_env/bin/activate
4. pip install django
5. django-admin --version
6. django-admin startproject tms

Instruction to initialize database:
1. sudo mysql
2. create database djangodatabase;
3. use djangodatabase;
4. create user dbadmin identified by '12345';
6. grant all PRIVILEGES on djangodatabase.* to 'dbadmin'@'%' with grant option;
7. flush privileges;
8. exit;

Connecting django with database:
1. sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
2. pip install mysqlclient
3. cd tms
4. Change DATABASES to the following in settings.py in django app
	DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangodatabase',
        'USER': 'dbadmin',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
5. Now go to parent directory using cd ..
6. python manage.py migrate
7. sudo mysql

Run django server:
1. python manage.py runserver


Youtube Channel : https://www.youtube.com/channel/UCYkO_D3Vi8KKJ8Wvtmnh-yw

