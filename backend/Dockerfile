FROM python:3.11-slim as builder
LABEL maintainer="André Felipe Dias <andref.dias@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev libxml2-dev \
    libxslt-dev curl libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# Poetry 1.4.0 has a bug that prevents it from installing Hypercorn
ENV POETRY_VERSION=1.3.1
RUN curl https://install.python-poetry.org | python -

RUN python -m venv /venv
ENV PATH=/venv/bin:/root/.local/bin:${PATH}

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN . /venv/bin/activate; \
    poetry install --only main --no-interaction

# ---------------------------------------------------------

FROM python:3.11-slim as final

COPY --from=builder /venv /venv
ENV PATH=/venv/bin:${PATH}
ENV ROOT_PATH=/

WORKDIR /app
USER nobody
COPY --chown=nobody:nogroup hypercorn.toml .
COPY --chown=nobody:nogroup selfsigned.* .
COPY --chown=nobody:nogroup transfer/ ./transfer

EXPOSE 5000

CMD hypercorn --config=hypercorn.toml --keyfile=selfsigned.key  \
    --certfile=/selfsigned.crt --root-path=${ROOT_PATH} transfer.main:app
