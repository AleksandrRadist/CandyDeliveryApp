# CandyDeliveryApp

REST API сервис, в котором можно нанимать курьеров на работу,
принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.

Проект использует:

    django - https://www.djangoproject.com
    django REST framework - https://www.django-rest-framework.org
    PostgreSQL - https://www.postgresql.org
 
## Installing

#### После подключения к серверу нужно

Обновить индексы пакетов APT:

    sudo apt update 

Обновить установленные в системе пакеты и установить обновление безопасности:

    sudo apt upgrade -y 
    
#### Далее подготовка базы данных
    
Установка PostgreSQL и необходимых для его работы пакетов:

    sudo apt install postgresql postgresql-contrib -y
    
Создание базы данных:

    sudo -u postgres psql
    CREATE DATABASE <db_name>;
    
Создание пользователя:
    
    CREATE USER <db_user> WITH ENCRYPTED PASSWORD '<db_user_password>';
    
Выдача необходимых прав:

    GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <db_user>;
    
Выдача прав для работы тестов:

    ALTER USER <db_user> CREATEDB;
    

#### Установка проекта
    
Установить необходимые пакеты:
    
    sudo apt install python3-pip python3-venv git -y 
    
Клонировать репозиторий:

    git clone https://github.com/AleksandrRadist/CandyDeliveryApp.git

Перейти в папку в папке проекта:
    
    cd CandyDeliveryApp/CandyDeliveryApp/
    
Создать и активировать виртуальное окружение:

    python3 -m venv venv
    . venv/bin/activate

Установить зависимости:

    python -m pip install -r requirements.txt

Создание .env с данными для подключения к базе данных:

    sudo nano /path-to-project-directory/CandyDeliveryApp/CandyDeliveryApp/CandyDeliveryApp/settings.py
    
Добавьте в файл данную строку:
    
    DATABASE_URL=psql://<db_user>:<db_user_password>@127.0.0.1:5432/<db_name>
        
Запустить миграции:
    
    python manage.py migrate
        
#### Запуск тестов

    python manage.py test
    
#### Запуск сервиса

Установка Gunicorn:
    
    pip install gunicorn

Создание юнита для сервера Gunicorn:

    sudo nano /etc/systemd/system/gunicorn.service

Внутри файла опишите следующую конфигурацию:

    [Unit] 
    Description=gunicorn daemon 
    After=network.target 

    [Service]
    User=<user_name>
    WorkingDirectory=/home/<user_name>/<path-to-project-directory> 
    ExecStart=<path-to-gunicorn-in-virtualenv>  --bind 0.0.0.0:8080 CandyDeliveryApp.wsgi:application

    [Install]
    WantedBy=multi-user.target

Запуск юнита:
    
    sudo systemctl start gunicorn

Добавление юнита в список автозапуска операционной системы:
    
    sudo systemctl enable gunicorn