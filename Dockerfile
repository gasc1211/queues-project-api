FROM python:3.12.7-bookworm AS builder

# Install poetry as package manager
RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_IN_PROJECT=1 \
POETRY_VIRTUALENVS_CREATE=1 \
POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

# Install project dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.12.7-bookworm AS runtime

# Install Dependencies for mssqlodbc18
RUN apt-get update && \
    apt-get -y install unzip && \
    apt-get -y install curl && \
    apt-get -y install gnupg && \
    apt-get -y install wget

# Install mssqlodbc18 connector
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
apt-get update && \
ACCEPT_EULA=Y apt-get install -y msodbcsql18

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY server ./server

ENTRYPOINT ["python", "-m", "server.main"]