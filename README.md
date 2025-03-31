# Short-URL-FastAPI: API-сервис сокращения ссылок

## Структура проекта 

Short-URL-FastAPI
├── docker
│   ├── app.sh
│   └── celery.sh
├── migrations
│   ├── versions
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── src
│   ├── auth
│   │   ├── auth.py
│   │   ├── db.py
│   │   ├── manager.py
│   │   └── schemas.py
│   ├── shorturl
│   │   ├── expired_link.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── tasks
│   │   ├── router.py
│   │   └── tasks.py
│   ├── utils
│   │   ├── security.py
│   │   └── short_code.py
│   ├── `__init__.py  
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── .env
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── logging.ini
├── requirements.txt
├── LICENSE
├── README.md
└── .gitignore

## 
