FROM python:3.6-jessie as base

# prepare
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y curl && \
    apt-get install -y unzip && \
    apt-get install -y build-essential && \
    apt-get install -y libfreetype6-dev && \
    apt-get install -y libhdf5-serial-dev && \
    apt-get install -y libpng-dev && \
    apt-get install -y libzmq3-dev && \
    apt-get install -y pkg-config


# Build
FROM base as builder

RUN pip install virtualenv

RUN virtualenv -p python3 /appenv

WORKDIR /var/src/

COPY requirements.txt .

RUN . /appenv/bin/activate; pip install -r requirements.txt

# run
FROM base

COPY --from=builder /appenv /appenv

WORKDIR /var/src/

COPY . .

ENTRYPOINT [ "sh" ]

EXPOSE 8000
