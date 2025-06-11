FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_PROJECT_ENVIRONMENT=/app/venv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

COPY --chown=app:app --from=builder /app/venv ./venv
COPY --chown=app:app ./backend/ .

COPY --chown=app:app ./scripts/ ./scripts 
RUN find ./scripts -type f -exec sed -i 's/\r$//g' {} \;
RUN find ./scripts/ -type f -exec chmod +x {} \;

USER app
CMD ["python", "-u", "manage.py", "runserver", "0.0.0.0:8000"]
