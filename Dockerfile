FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-prod.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --only-binary=:all: -r requirements-prod.txt

COPY . ./
RUN cp society_connect/settings/prod.sample.py society_connect/settings/prod.py \
    && chmod +x /app/docker/entrypoint.sh \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
