FROM python:3.6-alpine

COPY requirements.txt /tmp

RUN apk update \
    && apk add --virtual build-deps gcc musl-dev \
    && apk --no-cache add \
    wget \
    ca-certificates \
    wget \
    bash \
    zip \
    rsync \
    curl \
    postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

WORKDIR /opt/apps

RUN pip install -r /tmp/requirements.txt 

COPY app ./app
COPY migrations ./migrations
COPY config.py celery_worker.py manage.py bin/*.sh ./

ENTRYPOINT [ "sh" ]

CMD [ "./gunicorn.sh" ]