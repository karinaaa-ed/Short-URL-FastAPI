FROM python:3.10

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh

RUN mkdir -p /fastapi_app/migrations/versions
RUN chmod -R a+rw /fastapi_app/migrations
