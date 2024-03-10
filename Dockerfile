ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

RUN apt-get update && apt-get install -y nodejs npm

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY package.json package-lock.json ./
RUN npm install
COPY . /code

ENV SECRET_KEY "C0kGiiLVI7wae5qKdtEa7WN0yYCL1XPK11bBS3T9U7MHEn8AIy"
RUN python manage.py collectstatic --noinput
RUN apt-get update && apt-get install -y build-essential

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "elearning.asgi:application"]
