# Short-URL-FastAPI: API-сервис сокращения ссылок

## Структура проекта 

```
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
│   ├── __init__.py  
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── tests
│   ├── functional
│   │   ├── __init__.py  
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   ├── test_auth.py
│   │   └── test_links.py
│   ├── unit
│   │   ├── __init__.py  
│   │   ├── test_app.py
│   │   ├── test_main.py
│   │   ├── test_security.py
│   │   └── test_short_code.py
│   ├── __init__.py
│   ├── locustfile.py
│   ├── pytest.ini
│   └── test_tasks.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── logging.ini
├── requirements.txt
├── run_tests.sh
├── LICENSE
├── README.md
└── .gitignore
```

**1. Корневая директория** 
- `alembic.ini` – Конфигурационный файл для Alembic (миграции БД)
- `docker-compose.yml` – Конфигурация Docker Compose для запуска сервисов (FastAPI, Celery, Redis, PostgreSQL, Flower)
- `Dockerfile` – Инструкции для сборки Docker-образа приложения
- `logging.ini` – Настройки логгирования (формат, уровень логирования и т. д.)
- `requirements.txt` – Список зависимостей Python
- `run_tests.sh` - Скрипт для запуска тестов
- `LICENSE` – Лицензия проекта (Apache 2.0)
- `README.md` – Описание проекта, инструкции по запуску, документация
- `.gitignore` – Игнорируемые файлы и папки для Git

**2. Папка `docker/`**
- `app.sh` – Скрипт для запуска FastAPI-приложения (например, guvicorn)
- `celery.sh` – Скрипт для запуска Celery (фоновые задачи)

**3. Папка `migrations/`**

Файлы для миграций базы данных через Alembic:
- `versions/` – Папка с SQL-миграциями (создание/изменение таблиц)
- `env.py` – Конфигурация среды Alembic
- `README` – Описание работы с миграциями
- `script.py.mako` – Шаблон для генерации новых миграций 

**4. Папка `src/`**

Основной код приложения.
- Подпапка `auth/` – Аутентификация и авторизация:
  - `auth.py` – Логика аутентификации (OAuth2, JWT)
  - `db.py` – Модели и запросы к БД, связанные с пользователями
  - `manager.py` – Управление пользователями
  - `schemas.py` – Pydantic-схемы для запросов/ответов (регистрация, логин)
- Подпапка `shorturl/` – Логика сокращения URL:
  - `expired_link.py` – Удаление просроченных ссылок
  - `models.py` – SQLAlchemy-модели для URL
  - `router.py` – FastAPI-роутеры
  - `schemas.py` – Pydantic-схемы для URL (запросы, ответы)
- Подпапка `tasks/` – Фоновые задачи (Celery):
  - `router.py` – Роутеры для управления задачами
  - `tasks.py` – Сами задачи (очистка старых URL)
- Подпапка `utils/` – Вспомогательные модули:
  - `security.py` – Хеширование паролей, JWT-токены
  - `short_code.py` – Генерация коротких кодов для URL
- Остальные файлы в `src/`:
  - `__init__.py` – Делает папку Python-пакетом
  - `app.py` – Создание FastAPI-приложения
  - `config.py` – Загрузка настроек из .env
  - `database.py` – Подключение к БД (SQLAlchemy, asyncpg)
  - `main.py` – Точка входа (запуск `app.py`,  подключение роутеров)

**4. Папка `tests/`**

Тесты приложения.
- Подпапка `functional/` - Интеграционные тесты API:
  - `test_api.py`	- Тесты основных эндпоинтов
  - `test_auth.py` -	Тесты аутентификации
  - `test_links.py` -	Тесты для работы с ссылками
  - `conftest.py` -	Фикстуры для тестов
- Подпапка `unit/` - Юнит-тесты:
  - `test_app.py` -	Тесты для app.py
  - `test_main.py` -	Тесты для main.py
  - `test_security.py` -	Тесты утилит безопасности
  - `test_short_code.py` -	Тесты генерации коротких кодов
- Остальные файлы в `tests/`:
  - `locustfile.py` -	Нагрузочное тестирование с Locust
  - `pytest.ini` -	Конфигурация pytest (asyncio-режим)
  - `test_tasks.py` -	Тесты для фоновых задач


## Описание функционала API

API предоставляет следующие эндпоинты:

### `auth`
- **`/auth/jwt/login`**
  - Метод: **POST**
  - Описание: Авторизация пользователя
  - Пользователь должен заполнить следующие поля:
    - `grand_type` (необязательно) - Должен быть равен "password"
    - `username` (обязательно) – Email пользователя
    - `password` (обязательно) – Пароль пользователя
    - `scope` (необязательно) – Разрешения (scopes) (обычно не требуется)
    - `client_id` (необязательно) – Идентификатор клиента (обычно не требуется)
    - `client_secret` (необязательно) – Секрет клиента (обычно не требуется)
  - Возвращаемое значение: Токен пользователя

Пример ввода:

![image](https://github.com/user-attachments/assets/920ff074-b700-4b3c-b0ef-78c039a61d7d)

Пример вывода:

![image](https://github.com/user-attachments/assets/ee03adf0-0aad-46e3-a34e-120acf24f452)

- **`/auth/jwt/logout`**
  - Метод: **POST**
  - Описание: Выход пользователя из системы 

- **`/auth/jwt/register`**
  - Метод: **POST**
  - Описание: Регистрация нового пользователя. Принимает данные пользователя в формате JSON и создаёт новую запись в базе данных.
  - Пользователь должен заполнить все следующие поля:
    - `email` – Электронная почта пользователя. Также используется как логин.
    - `password` – Пароль пользователя.
    - `is_active` – Флаг активности аккаунта. Если false, пользователь не сможет войти.
    - `is_superuser` – Даёт права администратора (если true).
    - `is_verified` – Подтверждён ли email (если true).
    - `username` – Имя пользователя (в данном случае совпадает с email).
  - Возвращаемое значение: Подтверждение регистрации. Присваивание id.

Пример ввода:
```
{
    "email": "user123@example.com",
    "password": "password098",
    "is_active": true,
    "is_superuser": true,
    "is_verified": false,
    "username": "user123@example.com"
}
```

Пример вывода:

![image](https://github.com/user-attachments/assets/fba46682-2710-49fc-bee3-d8b631a9d78f)

### `Links`
- **`/links/shorten`**
  - Метод: **POST**
  - Описание: Создание короткой ссылки (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `original_url` – Длинный URL, который нужно сократить.
    - `custom_alias` – Пользовательский короткий идентификатор
      - Если не указан, сервер генерирует его автоматически.
      - Если указан, но уже занят, вернётся ошибка.
    - `expires_at` – Дата и время истечения срока действия ссылки (заполняется автоматически)
    - `project` –  Идентификатор проекта, с которым связана ссылка
  - Возвращаемое значение: Успешный статус 201 Created. Данные созданной короткой ссылки.

Пример ввода:
```
{
    "original_url": "https://colab.research.google.com/drive/1_XpbChmffd5u0k2c8TkOfAX3Y0MxU35",
    "custom_alias": "colab_hw3",
    "expires_at": "2026-03-31T14:36:52.1662",
    "project": "project123"
}
```
Пример вывода:
![image](https://github.com/user-attachments/assets/c617ac35-84e0-4734-8b29-0a2821f0c85b)

- **`/links/{short_code}`**
  - Метод: **GET**
  - Описание: Получение оригинального URL по короткой ссылке (для всех типов пользователей)
  - Пользователь должен заполнить следующие поля:
    - `short_code` – Короткая ссылка
  - Возвращаемое значение: Длинный исходный URL.

 Пример ввода:

 ![image](https://github.com/user-attachments/assets/110673bd-d1de-455e-9c44-43c731781d26)

- **`/links/{short_code}`**
  - Метод: **PUT**
  - Описание: Редактирование коротких ссылок (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `short_code` – Старая короткая ссылка
    - (Request body) `short_code` – Новая короткая ссылка
  - Возвращаемое значение: Данные по ссылке с новым коротким кодом.

Пример ввода:

![image](https://github.com/user-attachments/assets/7ceed4d0-5740-4e60-a59e-d29eea62f94a)

Пример вывода:

![image](https://github.com/user-attachments/assets/27aef169-354e-4f47-90ac-9982b87ae009)

- **`/links/{short_code}`**
  - Метод: **DELETE**
  - Описание: Удаление информации по короткой ссылке (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `short_code` – Короткая ссылка
  - Возвращаемое значение: Информация об успешном удалении ссылки и информации о ней.

Пример ввода:

![image](https://github.com/user-attachments/assets/8bfd3065-1b25-43f8-9b16-4114d487026c)

Пример вывода:

![image](https://github.com/user-attachments/assets/7e3bef41-8bde-4120-81ea-95123ecc5c8a)

- **`/links/{short_code}/stats`**
  - Метод: **GET**
  - Описание: Статистика по ссылке. Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования. (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `short_code` – Короткая ссылка
  - Возвращаемое значение: Информация о ссылке.

Пример ввода:

![image](https://github.com/user-attachments/assets/8e852fca-dc2d-45ee-8c47-81090f502c28)

Пример вывода:

![image](https://github.com/user-attachments/assets/e7b4156c-017a-4108-9583-e931f66ad562)

- **`/links/search`**
  - Метод: **GET**
  - Описание: Поиск ссылки по оригинальному URL. (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `original_url` – Исходная (оригинальная) ссылка
  - Возвращаемое значение: Информация о ссылке.

Пример ввода:

![image](https://github.com/user-attachments/assets/77727c98-d1bc-45c9-b947-b8d83d783bbe)

Пример вывода:

![image](https://github.com/user-attachments/assets/e7b4156c-017a-4108-9583-e931f66ad562)

- **`/links/projects/{project_name}`**
  - Метод: **GET**
  - Описание: Получение всех ссылок проекта. (только для зарегистрированных пользователей)
  - Пользователь должен заполнить следующие поля:
    - `project_name` – Название проекта
  - Возвращаемое значение: Информация о всех ссылках, зарегистированных в одном проекте.

Пример ввода:

![image](https://github.com/user-attachments/assets/93f789d6-9474-4f38-b042-0c565d4c1b97)

Пример вывода:

![image](https://github.com/user-attachments/assets/9573705c-cbe0-4cfd-96c3-a132cd3e00b0)

- **`/links/expired`**
  - Метод: **GET**
  - Описание: Получение истории истекших ссылок. (только для зарегистрированных пользователей)
  - Возвращаемое значение: Информация о ссылках с истекшим сроком (Если все ссылки действительны, то вернется пустой список)

Пример вывода:

![image](https://github.com/user-attachments/assets/aa278f96-bda6-41b4-98d1-ad7481585d50)

- **`/links/public/`**
  - Метод: **POST**
  - Описание: Создание короткой ссылки без аутентификации (для всех пользователей)
  - Пользователь должен заполнить следующие поля:
    - `original_url` – Длинный URL, который нужно сократить.
    - `expires_at` – Дата и время истечения срока действия ссылки (заполняется автоматически)
    - `project` –  Идентификатор проекта, с которым связана ссылка
  - Возвращаемое значение: Успешный статус 201 Created. Данные созданной короткой ссылки.

Пример ввода:

![image](https://github.com/user-attachments/assets/a148888b-2fc5-47cc-b79e-d5f98cd1232d)

Пример вывода:

![image](https://github.com/user-attachments/assets/00ece1aa-1d84-46a3-a0ba-b5bb9ff5140d)

### `report`

- **`/report/send`**
  - Метод: **GET**
  - Описание: Отправка сообщения пользователю. (только для зарегистрированных пользователей)
  - Возвращаемое значение: Информация об отправленном сообщении.

Пример вывода:

![image](https://github.com/user-attachments/assets/e571d89c-49da-4eae-a94f-65f15e6895de)

- **`/report/cleanup-links`**
  - Метод: **GET**
  - Описание: Очистка просроченных ссылок. (только для зарегистрированных пользователей)
  - Возвращаемое значение: Информация о том, что просроченные ссылки очищены.


## Инструкция по использованию

### Основные требования

- Версия Python 3.10+
- Установленный Docker
- Установленный PyCharm/VSCode

### Установка и запуск

**1. Клонирование репозитория**

Клонируйте репозиторий проекта:
```
git clone https://github.com/BELCHONOK-afk/Air_Quality_Prediction.git
cd service
```

**2. Установка зависимостей**

```
pip install -r requirements.txt
```

**3. Сборка и запуск контейнеров**


- Используйте `docker-compose` для запуска всех компонентов (FastAPI, Celery, Redis, PostgreSQL, Flower):
```
docker-compose up --build
```

- Создайте миграции и примените их:
```
docker-compose exec app alembic revision --autogenerate -m "Initial migration"
docker-compose exec app alembic upgrade head
```

- Проверить создание таблиц:
```
docker-compose exec db psql -U postgres -d postgres -c "\dt"
```

После успешного запуска документация будет доступна по адресу: `http://localhost:8000`.

**4. Запуск тестов**

**4.1. Запуск всех тестов**

Из корня проекта выполните:
```
pytest tests/
```

Или используйте скрипт:
```
./run_tests.sh
```

**4.2. Запуск отдельных групп тестов**

```
pytest tests/unit/              # юнит-тесты
pytest tests/functional/        # интеграционные тесты
```

Тесты для конкретного модуля

```
pytest tests/functional/test_links.py     # тесты для ссылок
pytest tests/unit/test_short_code.py      # тесты генерации кодов
```

**4.3. Нагрузочное тестирование (Locust)**

```
locust -f tests/locustfile.py
```

Откройте `http://localhost:8089` для управления тестом.


**5. Остановка контейнеров**

Для остановки всех сервисов выполните:
```
docker-compose down
```

### Данные по запуску

Запуск сервиса в PyCharm:

![image](https://github.com/user-attachments/assets/f9feebda-5db7-415b-ad62-60d3454026e9)

Созданный контейнер в Docker с выводом логов:

![image](https://github.com/user-attachments/assets/f9a50b2f-944d-4494-a5c8-45446fac248e)

Процент покрытия тестами:

![image](https://github.com/user-attachments/assets/977f5be6-5b3d-4f2e-9fbd-6304780cab0b)

