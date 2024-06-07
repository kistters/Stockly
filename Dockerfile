FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED 1
ENV PIPENV_SYSTEM=1

WORKDIR /app
EXPOSE 8080

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && pip install pipenv \
    && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /app/

FROM base as development
RUN pipenv install --deploy --ignore-pipfile --dev
COPY . /app/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

FROM base as production
RUN pipenv install --deploy --ignore-pipfile
COPY . /app/
CMD ["gunicorn", "--workers", "4", "--threads", "2", "-b", "0.0.0.0:8080", "--timeout", "60", "stockly.wsgi:application"]