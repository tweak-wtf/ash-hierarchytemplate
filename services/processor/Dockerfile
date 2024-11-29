FROM python:3.11-alpine3.18
ENV PYTHONUNBUFFERED=1

RUN mkdir /service
COPY pyproject.toml /service/pyproject.toml
WORKDIR /service

RUN \
  pip install -U pip && \
  pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

RUN addgroup -S ayonuser && adduser -SH ayonuser -G ayonuser

RUN chown ayonuser:ayonuser -R /service
RUN chmod 777 -R /service

COPY processor /service/processor

USER ayonuser

CMD ["python", "-m", "processor"]
