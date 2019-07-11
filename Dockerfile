FROM ubuntu:18.04 as builder
RUN apt-get update && \
    apt-get install -qyy \
    -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
    wget bash zip rsync python3.6 python3-venv python3-dev build-essential \
    python3-pip ca-certificates libpq-dev python-psycopg2 curl netcat netbase && \
    cd /usr/local/bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 
COPY requirements.txt .
RUN python3 -m venv appenv
RUN appenv/bin/pip install -r requirements.txt

FROM python:3.7-alpine
WORKDIR /opt/apps
COPY --from=builder /appenv ./appenv
RUN ls -lt .
COPY app ./app
COPY migrations ./migrations
COPY config.py celery_worker.py manage.py bin/*.sh ./
RUN . ./appenv/bin/activate
ENTRYPOINT [ "sh" ]
CMD [ "./gunicorn.sh" ]