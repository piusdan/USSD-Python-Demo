FROM ubuntu:18.04
RUN apt-get update && \
    apt-get install -qyy \
    -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
    python3-venv python3-dev build-essential \
    python3-pip libpq-dev python-psycopg2 && \
    cd /usr/local/bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /opt/apps
COPY . .
RUN python3 -m venv appenv
RUN appenv/bin/pip install -r requirements.txt
RUN . ./appenv/bin/activate
ENTRYPOINT [ "sh" ]
CMD [ "./start_app.sh" ]